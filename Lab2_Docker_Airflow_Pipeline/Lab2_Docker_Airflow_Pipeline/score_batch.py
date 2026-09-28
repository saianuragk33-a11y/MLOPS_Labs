import argparse,os
from pathlib import Path
import pandas as pd
from common import FEATURES
p=argparse.ArgumentParser();p.add_argument('input',nargs='?',default='/data/input.csv');p.add_argument('output',nargs='?',default='/data/scored.csv');p.add_argument('--lean',action='store_true');a=p.parse_args()
path=os.getenv('MODEL_DIR',str(Path(__file__).resolve().parent/'model_export'))
if a.lean:
    import joblib
    model=joblib.load(Path(path)/'model.joblib')
else:
    import mlflow.sklearn
    model=mlflow.sklearn.load_model(path)
d=pd.read_csv(a.input);d['churn_pred']=model.predict(d[FEATURES]);d['churn_probability']=model.predict_proba(d[FEATURES])[:,1]
d.to_csv(a.output,index=False);print(f'Scored {len(d)} customers -> {a.output}; churners={int(d.churn_pred.sum())}')
