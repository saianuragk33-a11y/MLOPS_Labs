import os,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
FEATURES=['tenure_months','monthly_spend','orders_per_month','support_tickets','uses_discounts','app_sessions']
EXPERIMENT=MODEL_NAME='cartvista-churn'
URI=os.getenv('MLFLOW_TRACKING_URI',f'sqlite:///{ROOT / "mlflow.db"}')
def setup():
    import mlflow
    mlflow.set_tracking_uri(URI)
    client=mlflow.MlflowClient()
    if client.get_experiment_by_name(EXPERIMENT) is None:
        client.create_experiment(EXPERIMENT,artifact_location=(ROOT/'mlruns').as_uri())
    mlflow.set_experiment(EXPERIMENT)
    return client
def fingerprint(path=None):
    return hashlib.md5(Path(path or ROOT/'churn_data.csv').read_bytes()).hexdigest()[:10]
def write_json(name,obj):
    p=ROOT/'evidence'/name;p.parent.mkdir(exist_ok=True)
    p.write_text(json.dumps(obj,indent=2,default=str));print(json.dumps(obj,indent=2,default=str))
