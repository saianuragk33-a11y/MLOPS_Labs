FROM python:3.11-slim
WORKDIR /app
COPY model_export/requirements.txt /tmp/model-requirements.txt
RUN pip install --no-cache-dir -r /tmp/model-requirements.txt
COPY model_export/ model_export/
COPY score_batch.py common.py ./
ENTRYPOINT ["python", "score_batch.py"]
