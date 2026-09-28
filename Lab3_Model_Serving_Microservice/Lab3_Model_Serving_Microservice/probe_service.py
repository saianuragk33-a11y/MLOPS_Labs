import argparse,requests
from common import write_json
RISK=dict(tenure_months=2,monthly_spend=2500.,orders_per_month=1,support_tickets=6,uses_discounts=0,app_sessions=2)
LOYAL=dict(tenure_months=60,monthly_spend=1500.,orders_per_month=8,support_tickets=0,uses_discounts=1,app_sessions=24)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8000');a=p.parse_args();out={}
    for name,path,payload in [('health','/health',None),('model','/model-info',None),('at_risk','/predict',RISK),('loyal','/predict',LOYAL),('invalid','/predict',dict(RISK,tenure_months=-5)),('empty_batch','/predict-batch',{'customers':[]})]:
        r=requests.get(a.url+path,timeout=30) if payload is None else requests.post(a.url+path,json=payload,timeout=30)
        out[name]={'status':r.status_code,'body':r.json()}
        if name in ['invalid','empty_batch']: assert r.status_code==422
        elif name!='health': r.raise_for_status()
    write_json('lab3_probes.json',out)
