import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score,accuracy_score
from common import ROOT,FEATURES
x=pd.read_csv(ROOT/'churn_data.csv')
a,b,c,d=train_test_split(x[FEATURES],x.churn,test_size=.25,random_state=42,stratify=x.churn)
m=RandomForestClassifier(n_estimators=50,max_depth=4,random_state=42).fit(a,c)
print('AUC=',roc_auc_score(d,m.predict_proba(b)[:,1]),'accuracy=',accuracy_score(d,m.predict(b)), 'always-no-churn accuracy=',1-d.mean())
