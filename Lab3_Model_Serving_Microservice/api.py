"""Shared validated serving engine. One worker for this teaching metrics design."""
import os,time,json,logging,random,threading
from collections import deque
from contextlib import asynccontextmanager
from pathlib import Path
import pandas as pd
import mlflow,mlflow.sklearn
from fastapi import FastAPI,HTTPException,Response
from pydantic import BaseModel,Field,ConfigDict
from prometheus_client import CollectorRegistry,Counter,Histogram,Gauge,generate_latest,CONTENT_TYPE_LATEST
from common import ROOT,FEATURES,MODEL_NAME,URI
from drift import psi

class Customer(BaseModel):
    model_config=ConfigDict(extra='forbid',allow_inf_nan=False)
    tenure_months:int=Field(ge=0,le=120)
    monthly_spend:float=Field(ge=0)
    orders_per_month:int=Field(ge=0)
    support_tickets:int=Field(ge=0)
    uses_discounts:int=Field(ge=0,le=1)
    app_sessions:int=Field(ge=0)
class BatchRequest(BaseModel):
    customers:list[Customer]=Field(min_length=1,max_length=10000)

def create_app(mode='plain'):
    state={};lock=threading.Lock();window=deque(maxlen=200);registry=CollectorRegistry()
    monitored=mode!='plain';ab=mode=='ab';shadow=os.getenv('SHADOW_MODE','0')=='1'
    split=float(os.getenv('CHALLENGER_SPLIT','.10'))
    if not 0<=split<=1: raise ValueError('CHALLENGER_SPLIT must be in [0,1]')
    pred=Counter('churn_predictions_total','Successful predictions',['outcome'],registry=registry)
    lat=Histogram('churn_inference_seconds','Single or batch inference seconds',buckets=[.001,.005,.01,.025,.05,.1,.25,.5,1],registry=registry)
    tickets=Gauge('churn_input_support_tickets','Last input ticket count',registry=registry)
    psig=Gauge('churn_tenure_psi','PSI of last 200 customer tenures',registry=registry)
    samples=Gauge('churn_psi_window_count','Samples currently in PSI window',registry=registry)
    baseline=Gauge('churn_training_base_rate','Training positive label fraction',registry=registry)
    abpred=Counter('ab_predictions_total','Model evaluations by variant and outcome',['variant','outcome'],registry=registry)
    ablat=Histogram('ab_inference_seconds','Model evaluation seconds',['variant'],buckets=[.001,.005,.01,.025,.05,.1,.25,.5,1],registry=registry)
    served=Counter('ab_served_total','Responses actually returned by variant',['variant'],registry=registry)
    for outcome in ['0','1']: pred.labels(outcome)
    for v in ['champion','challenger']:
        served.labels(v);ablat.labels(v)
        for o in ['0','1']: abpred.labels(v,o)
    def load(alias):
        exported=os.getenv('MODEL_DIR')
        if exported and not ab:
            p=Path(exported);meta=json.loads((p/'metadata.json').read_text())
            return mlflow.sklearn.load_model(str(p)),meta
        mlflow.set_tracking_uri(URI)
        if URI.startswith('sqlite:///') and not Path(URI[len('sqlite:///'):]).exists():
            raise FileNotFoundError('Registry database not found; run Lab 1')
        c=mlflow.MlflowClient();v=c.get_model_version_by_alias(MODEL_NAME,alias)
        # Resolve once; load the same immutable version that metadata reports.
        return mlflow.sklearn.load_model(f'models:/{MODEL_NAME}/{v.version}'),dict(model=MODEL_NAME,alias=alias,version=v.version,run_id=v.run_id)
    @asynccontextmanager
    async def lifespan(app):
        try:
            data=pd.read_csv(ROOT/'churn_data.csv') if (ROOT/'churn_data.csv').exists() else None
            if monitored and data is None: raise FileNotFoundError('Monitoring needs churn_data.csv baseline')
            if data is not None:
                state['reference']=data.tenure_months.to_numpy();baseline.set(float(data.churn.mean()))
            for v in (['champion','challenger'] if ab else ['champion']):
                state[v],state[v+'_info']=load(v)
            state['ready']=True
        except Exception as ex:
            state['ready']=False;state['error']=str(ex);logging.exception('Model startup degraded')
        yield
        state.clear()
    app=FastAPI(title='CartVista '+mode+' service',lifespan=lifespan)
    app.state.models=state
    def check():
        if not state.get('ready'): raise HTTPException(503,'Model unavailable; inspect /health and startup log')
    @app.get('/health')
    def health():
        return {'status':'ok' if state.get('ready') else 'degraded','model_loaded':bool(state.get('ready'))}
    @app.get('/model-info')
    def info():
        check()
        if ab: return {'mode':'shadow' if shadow else 'ab','challenger_split':split,**{v:state[v+'_info'] for v in ['champion','challenger']}}
        return state['champion_info']
    def evaluate(frame,v):
        start=time.perf_counter();m=state[v]
        # One probability pass; class rule agrees with sklearn binary argmax at ties.
        probability=m.predict_proba(frame)[:,1];predictions=(probability>.5).astype(int)
        elapsed=time.perf_counter()-start
        if ab:
            ablat.labels(v).observe(elapsed)
            for z in predictions: abpred.labels(v,str(int(z))).inc()
        return predictions,probability,elapsed
    def score(customers):
        check();frame=pd.DataFrame([c.model_dump() for c in customers],columns=FEATURES)
        variant='challenger' if ab and not shadow and random.random()<split else 'champion'
        predictions,probabilities,elapsed=evaluate(frame,variant)
        if ab:
            served.labels(variant).inc(len(customers))
            if shadow: evaluate(frame,'challenger')
        if monitored:
            lat.observe(elapsed)
            for z in predictions: pred.labels(str(int(z))).inc()
            tickets.set(customers[-1].support_tickets)
            with lock:
                window.extend(c.tenure_months for c in customers);samples.set(len(window))
                if len(window)>=20: psig.set(psi(state['reference'],list(window)))
        return predictions.tolist(),probabilities.tolist(),elapsed,variant
    @app.post('/predict')
    def predict(customer:Customer):
        predictions,probs,t,v=score([customer]);out={'churn_prediction':predictions[0],'churn_probability':probs[0],
            'model_version':state[v+'_info']['version'],'inference_ms':round(t*1000,3)}
        if ab: out['variant']=v;out['mode']='shadow' if shadow else 'ab'
        return out
    @app.post('/predict-batch')
    def batch(request:BatchRequest):
        predictions,probs,t,v=score(request.customers)
        return {'predictions':predictions,'probabilities':probs,'count':len(predictions),'model_version':state[v+'_info']['version'],'variant':v,'inference_ms':round(t*1000,3)}
    if monitored:
        @app.get('/metrics',include_in_schema=False)
        def metrics(): return Response(generate_latest(registry),media_type=CONTENT_TYPE_LATEST)
    return app
