# Lab 2 — Written explanations

## Lab 2

### Container concepts and result

The Dockerfile is the build recipe; an image is a packaged filesystem/environment; a container is a running instance. Layers allow Docker to cache dependency installation when only source code changes. The data volume keeps CSV inputs and scored outputs outside the immutable image. The model is baked into the scorer, making scoring independent of an available registry. Copying a pickle without matching its sklearn environment is not a reliable deployment strategy.

The full image loads the exported MLflow flavor. The lean image directly loads a trusted joblib export with the same sklearn/numpy/scipy versions and excludes the tracking/UI server dependencies. Both must produce identical labels and numerically matching probabilities. Record the actual byte sizes, convert them consistently to MB, and compute reduction = (before − after) / before × 100%. Do not equate compressed registry-download size with local uncompressed image size.

### Quality gate solution

Each training task returns its own successful run ID. validate_best receives only those two IDs, verifies successful status and consistent fingerprint/cycle, compares their test_auc, and returns the winning ID only if it passes the gate. Promotion consumes that exact ID. A query across the whole experiment can select an old good run and incorrectly pass today's failed training cycle; the solution avoids that bug. Setting the gate to 0.95 proves the dependency protection when promotion becomes upstream_failed and the old champion remains unchanged.

### E1 Retries and idempotency

A transient training failure is retryable because training does not send irreversible customer actions, though retries can create additional tracked runs. A task that sends retention emails can duplicate real messages when retried unless it uses a durable idempotency key and delivery record. In this solution the gate uses only the successful attempt's run ID, and promotion reuses an already registered version for that ID during retries. This reduces duplicate versions but is not a transaction spanning all possible concurrent registry writers.

### E2 Image reduction

The supplied Dockerfile.lean removes MLflow and its tracking/UI dependencies, uses --no-cache-dir, omits pandas, and includes only the joblib model and CSV/NumPy scoring source. It validates the trained feature order and retains numerical libraries required by inference. Record your measured before and after sizes and identical prediction check. If your architecture still exceeds 450 MB, report that result and perform further validated optimization; never claim an unmeasured size. Compatibility and correctness take precedence over blindly deleting shared libraries.

### E3 Monday cron and catchup

The expression 0 2 * * 1 selects minute 0, hour 2, every day-of-month/month, Monday. The timezone-aware start date makes the schedule Asia/Kolkata. catchup=False prevents an initial deployment from automatically retraining once for every missed historic interval. This is appropriate for the lab's current snapshot, where past intervals cannot be reconstructed from a versioned historical dataset. Airflow distinguishes data interval/logical date from the wall-clock time when a completed interval triggers a scheduled run; label the UI/CLI dates accurately in the report.

### E4 Containerized final task

The task exports champion after promotion, builds a tag containing the run ID and uses the host-visible named data volume. Rebuilding is necessary: exporting new files on the host alone does not update a previously built immutable image. A Docker daemon called from inside a container interprets bind paths in the daemon host's namespace, so using a shared named volume avoids a misleading /workspace host bind. The optional Docker socket configuration is confined to this local lab.

### E5 Failure callback

validate_best has an on_failure_callback that records UTC timestamp, Airflow run ID and the exception containing AUC and gate in evidence/gate_failures.log. Trigger a 0.95-gate run to generate actual evidence. A callback is not guaranteed delivery under every scheduler/process failure; production alerts need reliable external collection and monitoring of the orchestrator itself.

### Reflection What the gate misses

The gate protects promotion from an inadequate score on the evaluation snapshot. It does not detect future population drift, changed feature meanings, data leakage that inflates AUC, unfair performance across subgroups, service latency failures or an incorrect model artifact being deployed outside the gate. It also cannot prove causally improved retention. Production observation and appropriate labeled evaluation are complementary controls.

