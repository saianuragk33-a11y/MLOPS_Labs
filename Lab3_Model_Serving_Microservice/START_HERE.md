# Lab 3 — Model Serving Microservice

This is a separate runnable package and report for Lab 3. Open only this lab's folder and notebook. Do not submit the combined four-lab archive. The package includes prerequisite dataset/model creation; you do not have to copy a SQLite registry from another lab. No measured result or screenshot is prefilled.

## Start here: Windows / Docker route

1. Extract `Lab3_Model_Serving_Microservice.zip` into its own folder.
2. Open the extracted `Lab3_Model_Serving_Microservice` folder. Type `powershell` into File Explorer's address bar and press Enter.
3. Start Docker Desktop and wait for its engine. If it remains stuck on Starting, resolve the WSL startup issue first. Check these commands:

```text
python --version
docker info
docker compose version
```

4. Set your name:

```powershell
$env:LAB_AUTHOR="Sai YourFullName"
```

5. Initialize this lab once, then create its prerequisite dataset and registered champion:

```text
python labctl.py init
python labctl.py prepare
```

The prepare action runs the included training/registry scripts as setup. Their Lab 1 evidence is prerequisite material; it is not a second lab submission.

This lab uses Docker project `cartvista-lab3` and volume `cartvista_lab3_project`. Other labs use different volumes. Run one lab stack at a time because browser ports are shared. Run `python labctl.py stop` in the previous lab folder before starting another. Stopping preserves results. Do not add `-v` to Compose down unless you intend to delete data.

The detailed exercise commands follow. They run from this same folder.

## 5 Lab 3 REST prediction service

### 5.1 Start the plain API

Set the module in PowerShell:

```powershell
$env:SERVICE_MODULE="serve_churn"
```

macOS/Linux:

```bash
export SERVICE_MODULE=serve_churn
```

Then:

```text
docker compose up -d --force-recreate api
```

Open **http://localhost:8000/docs**. Expand each of the four endpoints: `/health`, `/model-info`, `/predict`, `/predict-batch`. Screenshot the docs. `/health` should return `status=ok` and `model_loaded=true`.

### 5.2 Run positive and negative examples

```text
docker compose run --rm tools python probe_service.py --url http://api:8000
docker compose run --rm tools python load_test.py --url http://api:8000
```

The probe sends the at-risk and loyal profiles, prints probabilities and model versions, and proves that negative tenure and empty batches receive HTTP 422. It also rejects unexpected extra fields and non-finite floats. A given profile's binary label depends on the learned model; inspect its probability rather than assuming every algorithm must match the brief's sample.

The load test discards 10 warm-up requests, measures 300 single calls with a persistent HTTP session, then compares them with three calls containing 100 customers each. It records p50/p95/p99/max, totals and speedup. This is sequential latency measurement, not a test of maximum concurrent throughput. Network timings include serialization and HTTP overhead; the response's `inference_ms` measures the model probability pass.

### 5.3 Alias hot-swap exercise

1. With the API running, visit `/model-info` and record version/run ID.
2. Register the best model again (this creates a new version; the weights may be identical):

```text
docker compose run --rm tools python register_model.py
```

3. Visit `/model-info` again. It still shows the old loaded version.
4. Restart the API:

```text
docker compose restart api
```

5. Visit `/model-info` again. It now shows the new version. Screenshot before and after. To demonstrate changed predictions as well, point the alias to a genuinely different model version; a version increment alone does not change weights.

The alias is resolved at startup. The implementation resolves the metadata once and loads that immutable version, preventing an alias-move race between loading and metadata lookup.

### 5.4 Baked-model service container

```text
python labctl.py export
docker build -f Dockerfile.service -t cartvista-api:v1 .
docker compose stop api
docker run --rm -p 127.0.0.1:8000:8000 cartvista-api:v1
```

Keep that terminal running. Visit `/health`, `/model-info` and `/docs`. This image contains the model and metadata and does not require your registry at inference time. Capture evidence, then Ctrl+C to stop it before using port 8000 again. A new champion requires re-exporting and rebuilding this image.

### 5.5 Missing-model graceful degradation

This equivalent non-destructive failure injection points to a missing model folder instead of renaming a live SQLite database:

```text
docker compose run --rm --service-ports -e MODEL_DIR=/missing-model api
```

Ensure any existing API is stopped first. `/health` returns HTTP 200 with `degraded` and `model_loaded=false`; a valid `/predict` request returns HTTP 503. Stop with Ctrl+C and restart the usual API. This process intentionally stays alive; the health body communicates degradation.

If your evaluator specifically requires the database rename from the brief, do it only on the local-Python route with all registry/UI processes stopped: rename `mlflow.db` to `mlflow.db.backup`, start the API, record the degraded/503 results, stop it, and rename the original back. The service checks that the database exists before connecting, so it does not silently create a replacement registry.


## Complete this lab's separate submission

1. Run `python labctl.py collect` to copy generated evidence into `my_results`.
2. Open this folder's `SUBMISSION_TEMPLATE.html`. It contains ONLY Lab 3 sections. Fill your name, ID and actual observations; add your screenshots using the image controls.
3. Read `WRITTEN_ANSWERS.md` for this lab's explanations. Adapt them to your measured outputs; do not invent values or successful UI runs.
4. Print the completed template to PDF as `Lab3_YourStudentID_Report.pdf` before closing the browser. Browser edits are not automatically saved to the HTML file.
5. Submit that PDF and the requested code/evidence for Lab 3 in its own portal entry. The starter ZIP is source material, not an executed submission. The course portal's required format takes precedence.
6. Use `python labctl.py stop` before starting another lab. Keep `my_results` and your PDF.

## Colab route for this lab

Upload `Lab3_Colab.ipynb` to Google Colab. In its first upload cell choose this lab's ZIP. Set your name, then run cells in order on a CPU runtime. Each notebook performs its own prerequisite training. Save the executed notebook and download its evidence ZIP before disconnecting.

Colab runs the actual API process, validation, latency and alias/restart exercises. The Docker image exercise still requires Docker.

## What is included

- This lab's instructions, written answers, notebook and editable report template.
- The required source scripts and infrastructure configuration.
- Shared model-generation scripts copied into this package so it can run independently.
- `VALIDATION.md`: checks performed and remaining execution requirements.

