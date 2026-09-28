"""Subcommands keep Airflow dependencies isolated from ML dependencies."""
import argparse,json
from common import setup,write_json
from register_model import register

def validate(ids,gate):
    c=setup();runs=[c.get_run(i) for i in ids]
    if len(runs)!=2 or any(r.info.status!='FINISHED' for r in runs): raise ValueError('Both current-cycle candidates must finish')
    if len({r.data.params['data_fingerprint'] for r in runs})!=1: raise ValueError('Candidates used different data')
    if len({r.data.tags.get('cycle_id') for r in runs})!=1: raise ValueError('Candidates are from different cycles')
    best=max(runs,key=lambda r:r.data.metrics['test_auc']);auc=best.data.metrics['test_auc']
    print(f'Current-cycle best AUC={auc:.6f}; gate={gate}; run={best.info.run_id}')
    if auc<gate: raise ValueError(f'Quality gate FAILED: {auc:.6f} < {gate}')
    return best.info.run_id
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['validate','promote']);p.add_argument('--run-ids',nargs='+',required=True);p.add_argument('--gate',type=float,default=.72);p.add_argument('--output');a=p.parse_args()
    if a.action=='validate':
        out={'run_id':validate(a.run_ids,a.gate)}
        if a.output:
            from pathlib import Path
            Path(a.output).write_text(json.dumps(out))
    else: register(a.run_ids[0],reuse=True)
