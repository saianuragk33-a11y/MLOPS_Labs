"""Manual tracking plus Lab 1 E1/E2/E3. Fixed split and data fingerprint."""
import argparse,os,json,time
import pandas as pd
import mlflow,mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.metrics import roc_auc_score,accuracy_score,f1_score,precision_score,recall_score
from mlflow.models import infer_signature
from common import ROOT,FEATURES,setup,fingerprint

def parser():
    p=argparse.ArgumentParser()
    p.add_argument('--model',choices=['logreg','rf','gb'],required=True)
    p.add_argument('--C',type=float,default=1.0)
    p.add_argument('--n-estimators',type=int,default=100)
    p.add_argument('--max-depth',type=int,default=6)
    p.add_argument('--learning-rate',type=float,default=.1)
    p.add_argument('--author',default=os.getenv('LAB_AUTHOR','Sai'))
    p.add_argument('--purpose',default='lab1-comparison')
    p.add_argument('--cycle',default='manual')
    p.add_argument('--output')
    return p

def train(a):
    setup()
    data=pd.read_csv(ROOT/'churn_data.csv')
    xtr,xte,ytr,yte=train_test_split(data[FEATURES],data.churn,test_size=.25,random_state=42,stratify=data.churn)
    if a.model=='logreg':
        model=LogisticRegression(C=a.C,max_iter=10000,random_state=42)
        hp={'C':a.C}
    elif a.model=='rf':
        hp={'n_estimators':a.n_estimators,'max_depth':a.max_depth}
        model=RandomForestClassifier(**hp,random_state=42,n_jobs=1)
    else:
        hp={'n_estimators':a.n_estimators,'learning_rate':a.learning_rate,'max_depth':a.max_depth}
        model=GradientBoostingClassifier(**hp,random_state=42)
    with mlflow.start_run(run_name=f'{a.model}-{a.purpose}') as run:
        mlflow.log_params(dict(hp,model_kind=a.model,data_fingerprint=fingerprint(),split_seed=42,test_size=.25))
        mlflow.set_tags({'author':a.author,'purpose':a.purpose,'cycle_id':a.cycle})
        t=time.perf_counter();model.fit(xtr,ytr)
        proba=model.predict_proba(xte)[:,1];pred=model.predict(xte)
        metrics={'test_auc':roc_auc_score(yte,proba),'test_accuracy':accuracy_score(yte,pred),
                 'test_f1':f1_score(yte,pred,zero_division=0),'test_precision':precision_score(yte,pred,zero_division=0),
                 'test_recall':recall_score(yte,pred,zero_division=0),'training_seconds':time.perf_counter()-t}
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(model,'model',signature=infer_signature(xtr,model.predict(xtr)),
            input_example=xtr.head(3),pip_requirements=['mlflow==2.14.1','scikit-learn==1.5.0','numpy==1.26.4','pandas==2.2.2','scipy==1.13.1','joblib==1.4.2','setuptools==70.1.0','SQLAlchemy==2.0.31'])
        result={'run_id':run.info.run_id,**metrics,'params':dict(hp,model_kind=a.model),'fingerprint':fingerprint()}
    if a.output:
        out=ROOT/a.output;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2));return result
if __name__=='__main__': train(parser().parse_args())
