FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from microservice folder and install
COPY microservices/technical-analysis-service/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy main.py
COPY microservices/technical-analysis-service/main.py ./main.py

# Copy analysis folder (shared, tech-analysis, LSTM, on chain)
COPY analysis ./analysis

# Optional: set Python path
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8001

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
