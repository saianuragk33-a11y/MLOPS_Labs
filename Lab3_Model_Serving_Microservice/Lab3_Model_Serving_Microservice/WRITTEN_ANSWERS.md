# Lab 3 — Written explanations

## Lab 3

### Online versus batch

Online prediction answers the checkout customer's request immediately; batch scoring processes a group of customers for a weekly outreach workflow. Both use the same six features and registered model, but the online service must manage request validation, availability, tail latency and stable schemas. The batch job can amortize initialization and I/O over thousands of rows.

### E1 Probability

predict_proba supplies the probability associated with class 1, enabling ranking or a business-specific threshold. A label discards most of that information. This estimator's probability is not automatically calibrated; a value of 0.8 should not be treated as a guaranteed 80% real-world frequency without calibration checks on suitable held-out data. The service exposes both the score and a 0.5-threshold label.

### E2 Why batching helps

Three requests with 100 customers each pay HTTP setup, JSON handling, validation, DataFrame construction and model-call overhead far fewer times than 300 individual requests. Vectorized estimator operations also amortize fixed computational overhead across rows. A persistent HTTP session is used for both paths to avoid attributing all differences to repeated TCP setup. The result is measured, not guaranteed: payload sizes, model type, network distance and hardware influence the speedup. End-to-end p95/p99 are the relevant experience metrics; average latency can hide a slow tail.

### E3 Alias resolution

The service resolves champion once during lifespan startup, obtains an immutable version and loads that exact version. Moving the registry alias does not modify the estimator object already resident in memory, so model-info remains unchanged until restart. This prevents an unplanned mid-process model change, but can leave a stale model serving indefinitely or different replicas serving different versions during a rolling restart. A controlled reload/rollout protocol and version-tagged telemetry are needed for production.

### E4 Container choice

We bake the exported model and its immutable metadata into the service image. This removes an inference-time dependency on the registry and makes a deployed image's model identity repeatable. Moving champion therefore requires re-export, image rebuild and a controlled redeployment, which trades instant updates for explicit releases.

### E5 Degraded startup

A failed model load is caught during startup. The process serves a health body indicating degraded state and refuses scoring with HTTP 503, rather than fabricating a prediction or crashing repeatedly. Invalid input still receives validation errors. A production platform should use a dedicated readiness probe that fails while the model is unavailable and a separate liveness probe for the process; this lab preserves the requested health response body.

### Reflection Two silent failures

First, a marketing campaign can change the live population to short-tenure, discount-heavy customers that were underrepresented at training time, reducing useful model performance while every HTTP request succeeds. Second, an upstream feature can silently change semantics—for example monthly spend arriving in another currency or orders_per_month changing to weekly orders—while keeping the same numeric type and passing schema validation. Data-distribution checks, schema/semantic contracts and delayed-label performance monitoring are needed to detect these cases.

