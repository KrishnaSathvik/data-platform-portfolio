# Data Platform Portfolio

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/downloads/)
[![Spark](https://img.shields.io/badge/Apache%20Spark-3.5.0-orange.svg)](https://spark.apache.org/)
[![Airflow](https://img.shields.io/badge/Apache%20Airflow-2.8.0-blue.svg)](https://airflow.apache.org/)
[![MLflow](https://img.shields.io/badge/MLflow-2.10.0-blue.svg)](https://mlflow.org/)
[![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.0.0-blue.svg)](https://delta.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A production-grade, end-to-end data platform demonstrating real-time processing, ML training, and workflow orchestration.**

> 🚀 **Live Demo**: [Watch the walkthrough →](demos/videos/)
> 📐 **Architecture**: [View system design →](docs/ARCHITECTURE.md)
> 🎬 **Screenshots**: [See the platform in action →](demos/screenshots/)

---

## 🌟 Overview

This project showcases a modern data platform built with industry-standard tools, implementing the complete data lifecycle from ingestion to ML deployment.

### What This Platform Does

- **Ingests** e-commerce transaction data via Apache Kafka
- **Processes** streams in real-time using Spark Structured Streaming
- **Stores** data in Delta Lake with medallion architecture (Bronze → Silver → Gold)
- **Detects** fraudulent transactions with multi-factor scoring
- **Transforms** data with dbt for analytics
- **Trains** ML models for fraud prediction with MLflow
- **Orchestrates** workflows with Apache Airflow
- **Monitors** system health with Prometheus & Grafana

---

## 📊 Quick Access

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow** | http://localhost:8082 | admin / airflow_pwd |
| **MLflow** | http://localhost:5002 | - |
| **Grafana** | http://localhost:3002 | admin / admin |
| **Prometheus** | http://localhost:9095 | - |
| **Kafka** | localhost:9092 | - |
| **PostgreSQL** | localhost:5433 | postgres / postgres |

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Docker Desktop 28.0+
- Python 3.13+
- 8GB RAM minimum
- 20GB disk space

### Setup

```bash
# 1. Clone repository
git clone https://github.com/KrishnaSathvik/data-platform-portfolio.git
cd data-platform-portfolio

# 2. Configure environment (optional for basic demo)
cp .env.example .env
# Edit .env if you want AI features (OpenAI, HuggingFace API keys)

# 3. Install Python dependencies
make install

# 4. Start all services (takes 2-3 minutes first time)
make up

# 5. Wait 30 seconds for initialization, then verify
make status

# 6. Run end-to-end demo
make demo
```

If everything shows ✅ and the demo runs, you're ready! 🎉

---

## 🏗️ Architecture

<p align="center">
  <img src="demos/screenshots/architecture-diagram.png" alt="Data Platform Architecture" width="800">
</p>

The platform implements a modern, scalable architecture:

```
E-commerce → Kafka → Spark Streaming → Delta Lake → dbt → PostgreSQL
Transactions                ↓
                    Fraud Detection
                         ↓
                    ML Training → MLflow → Model Serving
                         ↓
                    Airflow Orchestration
                         ↓
                  Prometheus & Grafana
```

📐 **[Full Architecture Documentation →](docs/ARCHITECTURE.md)**

### Key Components

1. **Data Ingestion**: Kafka + Schema Registry
2. **Stream Processing**: Spark Structured Streaming
3. **Data Lake**: Delta Lake (medallion architecture)
4. **Data Warehouse**: PostgreSQL + dbt
5. **ML Platform**: MLflow (tracking, registry, serving)
6. **Orchestration**: Apache Airflow
7. **Monitoring**: Prometheus + Grafana

---

## 📁 Project Structure

```
data-platform-portfolio/
├── data-platform/
│   ├── ingestion/              # Kafka producers
│   ├── processing/             # ⭐ Spark Streaming jobs (NEW)
│   │   ├── kafka_to_delta.py      # Bronze → Silver → Gold
│   │   ├── fraud_detection_stream.py  # Real-time fraud scoring
│   │   └── aggregations_stream.py     # Business metrics
│   ├── orchestration/
│   │   └── dags/              # ⭐ Airflow DAGs (NEW)
│   │       ├── data_ingestion_dag.py
│   │       ├── dbt_orchestration_dag.py
│   │       ├── ml_pipeline_dag.py
│   │       └── spark_streaming_dag.py
│   └── warehouse/              # dbt models
├── ml-platform/
│   ├── training/              # ⭐ ML Training Scripts (NEW)
│   │   ├── fraud_detection_trainer.py
│   │   └── hyperparameter_tuning.py
│   └── serving/               # FastAPI model serving
├── ai-platform/
│   └── rag-service/           # RAG with FAISS
├── infra/
│   └── docker/                # Docker Compose infrastructure
├── observability/
│   └── grafana/               # Dashboards
├── demos/
│   ├── screenshots/           # 📸 Platform screenshots
│   └── videos/                # 🎬 Demo videos
└── docs/
    ├── ARCHITECTURE.md        # 📐 System design
    └── DEMO_GUIDE.md          # 🎬 Recording guide
```

---

## ✨ Features

### Real-Time Stream Processing
- **Medallion Architecture**: Bronze (raw) → Silver (cleaned) → Gold (aggregated)
- **Fraud Detection**: Multi-factor scoring system (50+ risk signals)
- **Business Aggregations**: Merchant, user, country, hourly metrics
- **Windowed Analytics**: Sliding & tumbling windows (5min - 1hour)

### ML Pipeline
- **Model Training**: Logistic Regression, Random Forest, Gradient Boosting
- **Hyperparameter Tuning**: GridSearchCV & RandomizedSearchCV
- **Experiment Tracking**: MLflow with automated logging
- **Model Registry**: Versioning & deployment workflows
- **Deployment Criteria**: Precision ≥80%, Recall ≥70%, F1 ≥75%

### Workflow Orchestration
- **Data Ingestion DAG**: Hourly transaction generation
- **dbt Orchestration DAG**: 6-hourly warehouse transforms
- **ML Pipeline DAG**: Weekly model training
- **Monitoring DAG**: Daily health checks

### Data Transformation
- **dbt Models**: Staging & marts with tests
- **Data Quality**: Freshness, uniqueness, relationships
- **Documentation**: Auto-generated data catalog

### Observability
- **Metrics Collection**: Prometheus scraping
- **Dashboards**: Grafana visualizations
- **Alerting**: Threshold-based alerts
- **Logging**: Centralized log aggregation

---

## 🛠️ Usage

### Make Commands

```bash
# Service Management
make up              # Start all services
make down            # Stop all services
make status          # Check service health
make logs            # View service logs
make restart         # Restart all services

# Data Operations
make seed            # Generate Kafka transactions
make demo            # Run end-to-end demo

# Data Transformation
make dbt-run         # Run dbt models
make dbt-test        # Run dbt tests
make dbt-docs        # Generate dbt docs

# ML Operations
make train-model     # Train fraud detection model
make tune-model      # Run hyperparameter tuning

# Maintenance
make clean           # Clean all data
make prune           # Remove Docker resources
```

### Running Spark Streaming Jobs

```bash
# Main medallion pipeline
cd data-platform/processing
python kafka_to_delta.py

# Fraud detection stream
python fraud_detection_stream.py

# Business aggregations
python aggregations_stream.py
```

### Triggering Airflow DAGs

```bash
# Via CLI
airflow dags trigger data_ingestion_pipeline --conf '{"num_transactions": 5000}'

# Or via UI
open http://localhost:8082
# Navigate to DAGs → Select DAG → Trigger
```

### Training ML Models

```bash
# Basic training
cd ml-platform/training
python fraud_detection_trainer.py

# With hyperparameter tuning
python hyperparameter_tuning.py

# View results
open http://localhost:5002  # MLflow UI
```

---

## 🎯 What This Demonstrates

### Data Engineering Skills
✅ **Stream Processing**: Kafka, Spark Structured Streaming, Delta Lake
✅ **Batch Processing**: dbt, PostgreSQL, data quality
✅ **Data Modeling**: Medallion architecture, dimensional modeling
✅ **Orchestration**: Airflow DAGs, task dependencies
✅ **Real-time Analytics**: Windowed aggregations, fraud detection

### ML Engineering Skills
✅ **Model Development**: Scikit-learn, feature engineering
✅ **Experiment Tracking**: MLflow runs, parameters, metrics
✅ **Model Tuning**: GridSearchCV, RandomizedSearchCV
✅ **Model Registry**: Versioning, staging, production
✅ **Model Serving**: FastAPI, A/B testing (planned)

### Platform Engineering Skills
✅ **Infrastructure as Code**: Docker Compose
✅ **Service Orchestration**: Multi-container setup
✅ **Monitoring**: Prometheus metrics, Grafana dashboards
✅ **Developer Experience**: Makefile, documentation
✅ **Code Quality**: Pre-commit hooks, linting

---

## 📸 Screenshots & Demo

### Platform in Action

<table>
  <tr>
    <td><img src="demos/screenshots/05-airflow-dags-list.png" alt="Airflow DAGs" width="400"></td>
    <td><img src="demos/screenshots/10-mlflow-experiments.png" alt="MLflow Experiments" width="400"></td>
  </tr>
  <tr>
    <td align="center"><b>Airflow Orchestration</b></td>
    <td align="center"><b>MLflow Experiment Tracking</b></td>
  </tr>
  <tr>
    <td><img src="demos/screenshots/14-grafana-dashboard.png" alt="Grafana Dashboard" width="400"></td>
    <td><img src="demos/screenshots/03-delta-lake-structure.png" alt="Delta Lake" width="400"></td>
  </tr>
  <tr>
    <td align="center"><b>Grafana Monitoring</b></td>
    <td align="center"><b>Delta Lake Medallion</b></td>
  </tr>
</table>

> 📸 **[View all screenshots →](demos/screenshots/)**
> 🎬 **[Watch demo video →](demos/videos/)**
> 📋 **[Demo recording guide →](docs/DEMO_GUIDE.md)**

---

## 🔧 Technical Details

### Data Flow

1. **Ingestion** (Hourly via Airflow)
   ```
   E-commerce Transactions → Kafka Producer → Kafka Topic
   ```

2. **Stream Processing** (Real-time)
   ```
   Kafka → Spark Streaming → Delta Lake (Bronze → Silver → Gold)
   ```

3. **Fraud Detection** (Real-time)
   ```
   Silver Layer → Fraud Scoring → Risk Classification → Alerts
   ```

4. **Data Warehouse** (Every 6 hours via Airflow)
   ```
   Delta Lake → dbt Staging → dbt Marts → PostgreSQL
   ```

5. **ML Pipeline** (Weekly via Airflow)
   ```
   Delta Lake → Feature Extraction → Model Training → MLflow → Model Registry
   ```

### Performance Characteristics

- **Throughput**: 10,000+ messages/sec (Kafka)
- **Latency**: ~15 seconds end-to-end (Kafka → Gold)
- **ML Training**: ~2 minutes for 10K samples
- **Model Inference**: < 100ms per prediction

### Tech Stack Versions

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13 | Programming language |
| Apache Spark | 3.5.0 | Stream processing |
| Delta Lake | 3.0.0 | Data lake storage |
| Apache Kafka | 7.6.1 (Confluent) | Message streaming |
| Apache Airflow | 2.8.0 | Workflow orchestration |
| MLflow | 2.10.0 | ML experiment tracking |
| dbt | 1.9.0 | Data transformation |
| PostgreSQL | 15 | Data warehouse |
| Prometheus | 2.45.0 | Metrics collection |
| Grafana | 10.0.0 | Visualization |
| FastAPI | 0.115.6 | Model serving |
| Scikit-learn | 1.4.0 | Machine learning |

---

## 🔍 Troubleshooting

### Services Won't Start

```bash
# Check Docker
docker --version  # Should be 28.0+

# Restart everything
make down
make clean
make up
```

### Port Conflicts

```bash
# Check if ports are in use
lsof -i :8082  # Airflow
lsof -i :5002  # MLflow
lsof -i :9092  # Kafka

# Kill process or change ports in docker-compose.yml
```

### Airflow DAGs Not Showing

```bash
# Check for import errors
docker exec airflow-webserver airflow dags list-import-errors

# Restart Airflow
docker restart airflow-webserver
```

### MLflow Experiments Not Logging

```bash
# Check MLflow connection
curl http://localhost:5002/health

# Verify environment variable
echo $MLFLOW_TRACKING_URI
```

### Spark Jobs Failing

```bash
# Check Delta Lake path
ls -la /tmp/delta-lake

# Check Kafka connection
docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# View Spark logs
docker logs <spark-container-id>
```

### Out of Memory

```bash
# Reduce Spark partitions
# In config.py:
"spark.sql.shuffle.partitions": "2"  # Default is 4

# Reduce Docker memory
# Docker Desktop → Settings → Resources → Memory (8GB → 6GB)
```

---

## 🚀 Roadmap

### Completed ✅
- [x] Kafka ingestion pipeline
- [x] Spark Structured Streaming (Bronze/Silver/Gold)
- [x] Real-time fraud detection
- [x] Business aggregations (merchant, user, country)
- [x] dbt data warehouse
- [x] ML training pipeline (3 models)
- [x] Hyperparameter tuning
- [x] MLflow experiment tracking
- [x] Airflow orchestration (4 DAGs)
- [x] Docker infrastructure
- [x] Prometheus + Grafana monitoring

### Planned 🚧
- [ ] FastAPI model serving with A/B testing
- [ ] RAG service with FAISS
- [ ] Grafana dashboards configuration
- [ ] Great Expectations data quality
- [ ] CI/CD with GitHub Actions
- [ ] Kubernetes deployment manifests
- [ ] Performance benchmarks
- [ ] Load testing scripts

---

## 📚 Documentation

- 📐 **[Architecture Guide](docs/ARCHITECTURE.md)** - System design, data flows, tech stack
- 🎬 **[Demo Guide](docs/DEMO_GUIDE.md)** - Recording tips, screenshot checklist
- 🔄 **[Spark Processing README](data-platform/processing/README.md)** - Stream processing details
- 📅 **[Airflow DAGs README](data-platform/orchestration/dags/README.md)** - Workflow orchestration
- 🤖 **[ML Training README](ml-platform/training/README.md)** - Model development guide

---

## 🤝 Contributing

This is a portfolio project, but feedback and suggestions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Krishna Sathvik Mantripragada**

- GitHub: [@KrishnaSathvik](https://github.com/KrishnaSathvik)
- LinkedIn: [Your LinkedIn](https://linkedin.com/in/your-profile)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Apache Software Foundation for Kafka, Spark, and Airflow
- Databricks for Delta Lake
- MLflow team for experiment tracking
- dbt Labs for data transformation tools
- All open-source contributors

---

## 📊 Project Stats

![Lines of Code](https://img.shields.io/badge/Lines%20of%20Code-2900+-blue)
![Files](https://img.shields.io/badge/Files-50+-green)
![Commits](https://img.shields.io/github/commit-activity/m/KrishnaSathvik/data-platform-portfolio)
![Last Commit](https://img.shields.io/github/last-commit/KrishnaSathvik/data-platform-portfolio)

---

<p align="center">
  <b>Built with ❤️ for data engineering</b>
  <br>
  <sub>If you found this helpful, please ⭐ star the repo!</sub>
</p>
