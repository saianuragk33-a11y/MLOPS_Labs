import pandas as pd
import mlflow,mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from common import ROOT,FEATURES,setup
setup();d=pd.read_csv(ROOT/'churn_data.csv')
xtr,xte,ytr,yte=train_test_split(d[FEATURES],d.churn,test_size=.25,random_state=42,stratify=d.churn)
mlflow.sklearn.autolog()
with mlflow.start_run(run_name='autolog-comparison'):
    m=RandomForestClassifier(n_estimators=200,max_depth=8,random_state=42).fit(xtr,ytr)
    print('Held-out score',m.score(xte,yte))
