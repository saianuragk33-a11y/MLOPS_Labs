import argparse,tempfile,shutil,json
import mlflow.artifacts,mlflow.sklearn,joblib
from common import setup,MODEL_NAME,ROOT,FEATURES

def export(alias='champion'):
    c=setup();v=c.get_model_version_by_alias(MODEL_NAME,alias)
    dst=ROOT/'model_export'
    with tempfile.TemporaryDirectory() as td:
        src=mlflow.artifacts.download_artifacts(artifact_uri=f'runs:/{v.run_id}/model',dst_path=td)
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src,dst)
    model=mlflow.sklearn.load_model(str(dst));joblib.dump(model,dst/'model.joblib')
    (dst/'metadata.json').write_text(json.dumps({'model':MODEL_NAME,'alias':alias,'version':v.version,'run_id':v.run_id,'features':FEATURES},indent=2))
    print('Exported',v.version,'to',dst)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--alias',default='champion');export(p.parse_args().alias)
