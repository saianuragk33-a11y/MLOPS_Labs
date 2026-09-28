import numpy as np

def psi(expected,actual,bins=10):
    e=np.asarray(expected,dtype=float);a=np.asarray(actual,dtype=float)
    if not len(e) or not len(a) or not np.isfinite(e).all() or not np.isfinite(a).all():
        raise ValueError('PSI needs finite nonempty samples')
    # Unique quantiles avoid zero-width bins for discrete support-ticket data.
    u=np.unique(e)
    if len(u)<=bins:
        inner=(u[:-1]+u[1:])/2 if len(u)>1 else np.array([u[0]-.5,u[0]+.5])
    else:
        inner=np.unique(np.quantile(e,np.linspace(0,1,bins+1)[1:-1]))
    edges=np.r_[-np.inf,inner,np.inf]
    ec=np.histogram(e,edges)[0]+.5;ac=np.histogram(a,edges)[0]+.5
    ep=ec/ec.sum();ap=ac/ac.sum()
    return float(np.sum((ap-ep)*np.log(ap/ep)))
