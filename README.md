# Crypto Analytics Platform

Welcome to a full-stack cryptocurrency analytics platform built with a microservices architecture!

This platform combines real-time market data ingestion, technical indicator computation, LSTM-based price prediction, and on-chain sentiment analysis to give a comprehensive view of the crypto market. Each component runs as an independent service, making the system modular, scalable, and easy to extend.

## Getting Started

Clone the repository and start everything with Docker Compose:

```bash
git clone https://github.com/11ninaa/das-project.git
cd das-project
docker-compose up --build
```

The frontend will be available at `http://localhost` once all services are healthy.

If you want to enable news-based sentiment analysis, add your API keys before running:

```bash
export CRYPTOPANIC_API_KEY=your_key_here
export NEWSAPI_KEY=your_key_here
```

## Technologies Used

Python, JavaScript (React + Vite), Java Spring Boot, PostgreSQL, Docker

## Services

The platform is split into several microservices, each running independently:

| Service | Port | Description |
|---|---|---|
| Frontend | 80 | React + Vite user interface |
| Backend | 8080 | Spring Boot REST API |
| Data Ingestion | 8000 | Fetches real-time crypto market data |
| Technical Analysis | 8001 | Computes indicators like RSI, MACD, and moving averages |
| LSTM Prediction | 8002 | Deep learning model for price forecasting |
| Onchain Sentiment | 8003 | Sentiment analysis from crypto news sources |

## Project Structure

```
das-project/
├── frontend/crypto-app         # React + Vite frontend
├── backend/demo                # Spring Boot REST API
├── microservices/
│   ├── data-ingestion-service
│   ├── technical-analysis-service
│   ├── lstm-prediction-service
│   └── onchain-sentiment-service
├── crypto_etl/                 # ETL pipeline scripts
├── analysis/                   # Data analysis notebooks
└── docker-compose.yml
```

## Backend

The Spring Boot backend aggregates data from all Python microservices and exposes a unified REST API to the frontend. It connects to PostgreSQL and communicates with each service over the internal Docker network.

Run it standalone with:

```bash
cd backend/demo
mvn spring-boot:run
```

To point the frontend at a local backend instance, set the API URL in your environment:

```
VITE_API_BASE_URL=http://localhost:8080
```
