FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*


COPY microservices/lstm-prediction-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY microservices/lstm-prediction-service/main.py .

COPY analysis ./analysis

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]

