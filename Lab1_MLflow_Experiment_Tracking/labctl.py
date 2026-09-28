"""Cross-platform Docker helper. Only Python's standard library is needed."""
import subprocess,sys,os,argparse,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def call(*args): subprocess.run(list(args),cwd=ROOT,check=True)
def compose(*args): call('docker','compose',*args)
def ml(*args): compose('run','--rm','tools','python',*args)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init', 'lab1', 'collect', 'stop']);a=p.parse_args()
    if a.action=='init':
        compose('build','tools')
        # Copy code into a portable shared volume: every process sees /workspace.
        compose('run','--no-deps','--name','cartvista-lab1-bootstrap','--user','0:0','-d','tools','sleep','infinity')
        try:
            for item in ROOT.iterdir():
                if item.name in ['.venv','mlruns','model_export','evidence','__pycache__','.pytest_cache'] or item.name.startswith('mlflow.db'): continue
                call('docker','cp',str(item),'cartvista-lab1-bootstrap:/workspace/'+item.name)
            call('docker','exec','cartvista-lab1-bootstrap','sh','-c','mkdir -p /workspace/evidence && chmod -R g+rwX /workspace')
        finally: call('docker','rm','-f','cartvista-lab1-bootstrap')
        print('Initialized. Run python labctl.py lab1 next. Do not repeat init on an active project.')
    elif a.action in ['lab1','prepare']: ml('run_lab1.py')
    elif a.action in ['export','scorer']:
        ml('export_champion.py')
        compose('run','--no-deps','--name','cartvista-lab1-copy','-d','tools','sleep','infinity')
        try:
            if (ROOT/'model_export').exists(): shutil.rmtree(ROOT/'model_export')
            call('docker','cp','cartvista-lab1-copy:/workspace/model_export',str(ROOT/'model_export'))
        finally: call('docker','rm','-f','cartvista-lab1-copy')
        if a.action=='scorer':
            call('docker','build','-t','cartvista-scorer:v1','.')
            call('docker','build','-f','Dockerfile.lean','-t','cartvista-scorer:lean','.')
            for tag,out in [('v1','scored.csv'),('lean','scored_lean.csv')]:
                call('docker','run','--rm','--user','50000:0','-v','cartvista_lab1_project:/data','cartvista-scorer:'+tag,'/data/churn_data.csv','/data/'+out)
            call('docker','images','cartvista-scorer')
            ml('-c',"import pandas as pd,numpy as np; a=pd.read_csv('scored.csv'); b=pd.read_csv('scored_lean.csv'); assert (a.churn_pred==b.churn_pred).all(); assert np.allclose(a.churn_probability,b.churn_probability); print('Full and lean predictions match')")
    elif a.action=='collect':
        compose('run','--no-deps','--name','cartvista-lab1-copy','-d','tools','sleep','infinity')
        dest=ROOT/'my_results';dest.mkdir(exist_ok=True)
        try:
            for name in ['evidence','model_export','churn_data.csv','scored.csv','scored_lean.csv','scored_weekly.csv']:
                exists=subprocess.run(['docker','exec','cartvista-lab1-copy','test','-e','/workspace/'+name],cwd=ROOT).returncode==0
                if not exists: continue
                if name in ['evidence','model_export']:
                    (dest/name).mkdir(exist_ok=True)
                    call('docker','cp','cartvista-lab1-copy:/workspace/'+name+'/.',str(dest/name))
                else:
                    call('docker','cp','cartvista-lab1-copy:/workspace/'+name,str(dest/name))
        finally: call('docker','rm','-f','cartvista-lab1-copy')
        print('Saved evidence in',dest)
    elif a.action=='stop': compose('down')
