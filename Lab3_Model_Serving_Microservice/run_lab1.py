"""Run from a fresh folder for a clean experiment table. Re-runs add runs."""
import subprocess,sys,json
from common import ROOT,write_json

def run(*args): subprocess.run([sys.executable,*args],cwd=ROOT,check=True)
if __name__=='__main__':
    run('generate_data.py');run('train_no_tracking.py')
    for c in [.1,1.,10.]: run('train_tracked.py','--model','logreg','--C',str(c))
    for n,d in [(50,4),(200,8),(400,12)]: run('train_tracked.py','--model','rf','--n-estimators',str(n),'--max-depth',str(d))
    run('register_model.py');run('consume_model.py')
    # E1 explicitly rerun the current best configuration with the added metrics.
    from common import setup,MODEL_NAME
    c=setup();v=c.get_model_version_by_alias(MODEL_NAME,'champion');params=c.get_run(v.run_id).data.params
    extra=['--model',params['model_kind'],'--purpose','lab1-E1']
    for key,flag in [('C','--C'),('n_estimators','--n-estimators'),('max_depth','--max-depth'),('learning_rate','--learning-rate')]:
        if key in params: extra.extend([flag,params[key]])
    run('train_tracked.py',*extra)
    # All manual runs already log precision, recall and author/purpose.
    for n,lr in [(100,.05),(200,.1)]:
        run('train_tracked.py','--model','gb','--n-estimators',str(n),'--max-depth','3','--learning-rate',str(lr),'--purpose','lab1-E2')
    run('register_model.py')
    # E4: remove exactly one data row; restore even if training raises.
    p=ROOT/'churn_data.csv';original=p.read_bytes()
    try:
        import pandas as pd
        from common import fingerprint
        before=fingerprint();pd.read_csv(p).iloc[:-1].to_csv(p,index=False)
        after=fingerprint();run('train_tracked.py','--model','logreg','--purpose','lab1-E4-modified-data')
        write_json('lab1_fingerprints.json',{'before':before,'after':after,'rows_removed':1})
    finally: p.write_bytes(original)
    run('train_auto.py');run('consume_model.py')
