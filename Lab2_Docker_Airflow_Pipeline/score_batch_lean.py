"""Minimal scorer: CSV + NumPy; no pandas or MLflow dependency."""
import csv,sys,warnings
from pathlib import Path
import numpy as np,joblib
FEATURES=['tenure_months','monthly_spend','orders_per_month','support_tickets','uses_discounts','app_sessions']
source=sys.argv[1] if len(sys.argv)>1 else '/data/input.csv'
target=sys.argv[2] if len(sys.argv)>2 else '/data/scored.csv'
with open(source,newline='') as f:
    reader=csv.DictReader(f);fieldnames=reader.fieldnames;rows=list(reader)
if not rows: raise ValueError('Input CSV must contain at least one customer')
if not set(FEATURES).issubset(fieldnames): raise ValueError('Missing required features')
model=joblib.load(Path(__file__).resolve().parent/'model_export/model.joblib')
if hasattr(model,'feature_names_in_') and list(model.feature_names_in_)!=FEATURES:
    raise ValueError('Model feature order differs from scorer contract')
x=np.array([[float(row[col]) for col in FEATURES] for row in rows],dtype=float)
if not np.isfinite(x).all(): raise ValueError('Nonfinite input')
# We validate feature order above; sklearn warns only because ndarray lacks labels.
with warnings.catch_warnings():
    warnings.filterwarnings('ignore',message='X does not have valid feature names')
    pred=model.predict(x);proba=model.predict_proba(x)[:,1]
columns=[k for k in fieldnames if k not in ['churn_pred','churn_probability']]+['churn_pred','churn_probability']
with open(target,'w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader()
    for row,p,q in zip(rows,pred,proba):
        row.update(churn_pred=int(p),churn_probability=float(q));writer.writerow(row)
print(f'Scored {len(rows)} customers -> {target}; churners={int(pred.sum())}')
