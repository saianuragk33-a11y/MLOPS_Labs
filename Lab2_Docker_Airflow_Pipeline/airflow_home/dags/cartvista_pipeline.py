"""Diamond DAG; current-run IDs travel through XCom, never historical best."""
from datetime import timedelta
from pathlib import Path
import subprocess,json,hashlib,os
import pendulum
from airflow.decorators import dag,task
from airflow.operators.python import get_current_context

PROJECT=Path('/workspace')
PY='/opt/mlvenv/bin/python'
def run(*args):
    r=subprocess.run([PY,*args],cwd=PROJECT,text=True,capture_output=True)
    print(r.stdout);print(r.stderr);r.check_returncode();return r.stdout

def failure(context):
    with (PROJECT/'evidence/gate_failures.log').open('a') as f:
        f.write(f"{pendulum.now('UTC').isoformat()} run={context['run_id']} exception={context.get('exception')}\n")

@dag(schedule='0 2 * * 1',start_date=pendulum.datetime(2026,1,1,tz='Asia/Kolkata'),
     catchup=False,max_active_runs=1,tags=['cartvista'])
def cartvista_weekly_retrain():
    @task
    def refresh_data():
        ctx=get_current_context();cycle=ctx['run_id']
        folder=PROJECT/'evidence'/'pipeline'/hashlib.sha256(cycle.encode()).hexdigest()[:16]
        folder.mkdir(parents=True,exist_ok=True)
        run('generate_data.py')
        # Initialize experiment once, before parallel candidate tracking.
        run('-c','from common import setup; setup()')
        return {'cycle':cycle,'folder':str(folder)}
    @task(retries=2,retry_delay=timedelta(seconds=30))
    def train_candidate(config,kind):
        out=Path(config['folder'])/(kind+'.json')
        args=['train_tracked.py','--model',kind,'--purpose','lab2-weekly','--cycle',config['cycle'],'--output',str(out)]
        args+=['--C','1'] if kind=='logreg' else ['--n-estimators','200','--max-depth','8']
        run(*args);return json.loads(out.read_text())['run_id']
    @task(on_failure_callback=failure)
    def validate_best(config,lr_id,rf_id):
        threshold=float((get_current_context()['dag_run'].conf or {}).get('auc_gate',.72))
        out=Path(config['folder'])/'validated.json'
        run('pipeline_cli.py','validate','--run-ids',lr_id,rf_id,'--gate',str(threshold),'--output',str(out))
        return json.loads(out.read_text())['run_id']
    @task
    def promote(run_id):
        run('pipeline_cli.py','promote','--run-ids',run_id)
        return run_id
    @task
    def score_weekly(run_id):
        # Stretch E4. Base compose completes without granting Docker access.
        conf=get_current_context()['dag_run'].conf or {}
        if not conf.get('score_container',False):
            print('E4 disabled. Trigger with score_container=true and optional Docker override.');return
        run('export_champion.py')
        tag='cartvista-scorer:weekly-'+run_id[:8]
        subprocess.run(['docker','build','-f','Dockerfile.lean','-t',tag,'.'],cwd=PROJECT,check=True)
        # Named volume exists in the HOST daemon namespace (not container paths).
        volume=os.getenv('PROJECT_DOCKER_VOLUME','cartvista_lab2_project')
        subprocess.run(['docker','run','--rm','-v',volume+':/data',tag,'/data/churn_data.csv','/data/scored_weekly.csv'],check=True)
    config=refresh_data()
    lr=train_candidate.override(task_id='train_logreg')(config,'logreg')
    rf=train_candidate.override(task_id='train_rf')(config,'rf')
    score_weekly(promote(validate_best(config,lr,rf)))
cartvista_weekly_retrain()
