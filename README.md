# Data Platform Portfolio

Full-Stack Data Platform Engineer bootcamp project - a complete data + AI platform built from scratch.

## 🚀 Quick Start (5 minutes)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your API keys (optional for basic demo)

# 2. Install dependencies
make install

# 3. Start all services
make up

# 4. Wait 30 seconds, then verify
make status

# 5. Run end-to-end demo
make demo
```

If everything shows "OK" and the demo runs, you're ready! 🎉

## 📊 Service URLs

- **Grafana:** http://localhost:3002 (admin/admin)
- **MLflow:** http://localhost:5002
- **Airflow:** http://localhost:8082 (admin/admin)
- **Prometheus:** http://localhost:9095
- **Schema Registry:** http://localhost:8081

## 🏗️ Architecture

This platform demonstrates:

- **Real-time Data Processing:** Kafka → Spark → Delta Lake
- **Analytics Warehouse:** dbt → PostgreSQL with quality tests
- **ML Platform:** MLflow + FastAPI with A/B testing
- **AI Platform:** RAG service with FAISS + sentence transformers
- **Observability:** Prometheus + Grafana monitoring

## 📁 Project Structure

```
data-platform-portfolio/
├── infra/docker/          # All infrastructure as code
├── data-platform/         # Data ingestion, processing, warehouse
├── ml-platform/           # Model training and serving
├── ai-platform/           # RAG and AI services  
├── observability/         # Monitoring and dashboards
└── demos/                 # Documentation and demos
```

## 🛠️ Available Commands

```bash
make up          # Start all services
make down        # Stop all services  
make status      # Check service health
make demo        # Run end-to-end demo
make logs        # View service logs
make seed        # Send sample data to Kafka
make dbt-run     # Run dbt transformations
make clean       # Clean everything
```

## 🎯 What This Demonstrates

### Data Engineering
- Event streaming with Kafka and Schema Registry
- Real-time processing with Spark Structured Streaming
- Data lake with Delta Lake (bronze/silver/gold)
- Analytics warehouse with dbt and quality testing
- Workflow orchestration with Airflow

### ML Engineering  
- Experiment tracking with MLflow
- Model serving with FastAPI and A/B testing
- Model monitoring and performance tracking

### AI Engineering
- RAG (Retrieval Augmented Generation) with FAISS
- Vector search and semantic similarity
- AI explanation generation for ML predictions

### Platform Engineering
- Infrastructure as Code with Docker Compose
- Service discovery and networking
- Monitoring with Prometheus and Grafana
- Health checks and observability
- Developer experience with Make commands

## 🔧 Troubleshooting

### Services won't start
```bash
make down
make clean
make up
```

### Connection issues
```bash
make status  # Check which services are down
make logs    # View error logs
```

### Out of disk space
```bash
docker system prune -f
```

## 📈 Next Steps

This is the foundation for an 8-week bootcamp that builds:

1. **Weeks 1-2:** Data platform with streaming and warehouse
2. **Weeks 3-4:** ML platform with training and serving  
3. **Weeks 5-6:** AI platform with RAG and explanations
4. **Weeks 7-8:** Production hardening and job search

Ready to become a Full-Stack Data Platform Engineer! 🚀
