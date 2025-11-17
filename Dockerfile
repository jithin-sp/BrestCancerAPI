# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# system deps for xgboost sometimes
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app and model files
COPY app.py /app/app.py
COPY models /app/models

ENV MODEL_DIR=/app/models
ENV PORT=10000

EXPOSE 10000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
