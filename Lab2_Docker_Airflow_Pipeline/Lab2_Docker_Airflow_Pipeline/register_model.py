import argparse
import mlflow
from common import setup,EXPERIMENT,MODEL_NAME,fingerprint,write_json

def register(run_id=None,alias='champion',reuse=False):
    c=setup()
    if not run_id:
        exp=c.get_experiment_by_name(EXPERIMENT)
        runs=c.search_runs([exp.experiment_id],filter_string=f"attributes.status = 'FINISHED' and params.data_fingerprint = '{fingerprint()}'",order_by=['metrics.test_auc DESC'],max_results=100)
        runs=[r for r in runs if 'test_auc' in r.data.metrics]
        if not runs: raise RuntimeError('No finished comparable runs. Run Lab 1 first.')
        run_id=runs[0].info.run_id
    r=c.get_run(run_id)
    if r.info.status!='FINISHED': raise ValueError('Refusing unfinished run')
    # Reuse a version on retries; alias update is repeatable.
    versions=[v for v in c.search_model_versions(f"name='{MODEL_NAME}'") if v.run_id==run_id]
    mv=versions[0] if reuse and versions else mlflow.register_model(f'runs:/{run_id}/model',MODEL_NAME)
    c.set_registered_model_alias(MODEL_NAME,alias,mv.version)
    out={'alias':alias,'version':mv.version,'run_id':run_id,'test_auc':r.data.metrics.get('test_auc')}
    write_json(f'{alias}.json',out);return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run-id');p.add_argument('--alias',default='champion');a=p.parse_args();register(a.run_id,a.alias)
