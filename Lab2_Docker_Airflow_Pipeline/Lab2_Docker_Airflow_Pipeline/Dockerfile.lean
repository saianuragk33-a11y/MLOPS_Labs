FROM python:3.11-slim
WORKDIR /app
COPY requirements-lean.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY model_export/model.joblib /app/model_export/model.joblib
COPY score_batch_lean.py ./
ENTRYPOINT ["python", "score_batch_lean.py"]
