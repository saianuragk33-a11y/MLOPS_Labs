import mlflow.sklearn,pandas as pd
from common import setup,MODEL_NAME,ROOT,FEATURES,write_json
c=setup();v=c.get_model_version_by_alias(MODEL_NAME,'champion')
m=mlflow.sklearn.load_model(f'models:/{MODEL_NAME}/{v.version}')
x=pd.read_csv(ROOT/'churn_data.csv')[FEATURES].head(5)
write_json('lab1_consume.json',{'version':v.version,'run_id':v.run_id,'predictions':m.predict(x).tolist(),'probabilities':m.predict_proba(x)[:,1].tolist()})
