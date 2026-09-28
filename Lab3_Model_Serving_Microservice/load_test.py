import argparse,time,numpy as np,requests
from common import write_json
from probe_service import LOYAL
p=argparse.ArgumentParser();p.add_argument('--url',default='http://127.0.0.1:8000');a=p.parse_args()
with requests.Session() as s:
    def request(path,payload):
        r=s.post(a.url+path,json=payload,timeout=60);r.raise_for_status();return r.json()
    for _ in range(10): request('/predict',LOYAL)
    lat=[];start=time.perf_counter()
    for _ in range(300):
        t=time.perf_counter();request('/predict',LOYAL);lat.append(1000*(time.perf_counter()-t))
    single=time.perf_counter()-start
    request('/predict-batch',{'customers':[LOYAL]*100})
    start=time.perf_counter()
    for _ in range(3): assert request('/predict-batch',{'customers':[LOYAL]*100})['count']==100
    batch=time.perf_counter()-start
write_json('lab3_latency.json',{'n':300,'warmup':10,'p50_ms':np.percentile(lat,50),'p95_ms':np.percentile(lat,95),'p99_ms':np.percentile(lat,99),'max_ms':max(lat),'single_300_seconds':single,'batch_3x100_seconds':batch,'speedup':single/batch})
