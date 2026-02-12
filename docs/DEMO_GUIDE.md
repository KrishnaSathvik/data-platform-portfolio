# Demo Guide - Data Platform Portfolio

This guide will help you create a compelling demo video and take screenshots for your portfolio.

## Pre-Demo Checklist

Before starting your demo, ensure:
- [ ] All Docker services are running (`docker ps`)
- [ ] Airflow UI accessible at http://localhost:8082
- [ ] MLflow UI accessible at http://localhost:5002
- [ ] Grafana accessible at http://localhost:3002
- [ ] Prometheus accessible at http://localhost:9095

## Demo Video Script (8-10 minutes)

### Introduction (30 seconds)
**Script**:
> "Hi, I'm [Your Name], and today I'll walk you through my end-to-end data platform portfolio project. This platform demonstrates real-time data processing, ML training, and orchestration using modern data engineering tools like Kafka, Spark, Delta Lake, Airflow, and MLflow."

**What to show**:
- Architecture diagram from `docs/ARCHITECTURE.md`

---

### Part 1: Data Ingestion (2 minutes)

**Script**:
> "Let's start with data ingestion. We're simulating e-commerce transactions that flow into Kafka."

**Steps to demonstrate**:

1. **Show Kafka Producer**
   ```bash
   cd data-platform/ingestion
   python seed_events.py
   ```
   - Show the console output of transactions being generated
   - Explain the transaction schema (user_id, amount, merchant, etc.)

2. **Verify Kafka Topic**
   ```bash
   docker exec kafka kafka-topics --bootstrap-server localhost:9092 --list
   docker exec kafka kafka-console-consumer --bootstrap-server localhost:9092 \
       --topic ecommerce.transactions --from-beginning --max-messages 5
   ```
   - Show real messages in Kafka
   - Point out the Avro schema

**Screenshot locations**:
- `demos/screenshots/01-kafka-producer.png` - Terminal showing transaction generation
- `demos/screenshots/02-kafka-messages.png` - Console consumer output

---

### Part 2: Real-time Stream Processing (2 minutes)

**Script**:
> "These transactions are processed in real-time using Spark Structured Streaming with a medallion architecture: Bronze, Silver, and Gold layers."

**Steps to demonstrate**:

1. **Show Spark Streaming Job** (if running)
   - Explain Bronze layer (raw data)
   - Explain Silver layer (cleaned & enriched)
   - Explain Gold layer (aggregations)

2. **Show Delta Lake Tables**
   ```bash
   ls -lh /tmp/delta-lake/bronze/transactions
   ls -lh /tmp/delta-lake/silver/transactions
   ls -lh /tmp/delta-lake/gold/transactions
   ```
   - Show the _delta_log directory
   - Explain ACID transactions

3. **Demo Fraud Detection**
   ```bash
   cd data-platform/processing
   # Show the fraud_detection_stream.py code briefly
   cat fraud_detection_stream.py | head -50
   ```
   - Explain the fraud scoring system
   - Show risk classifications (CRITICAL/HIGH/MEDIUM/LOW/MINIMAL)

**Screenshot locations**:
- `demos/screenshots/03-delta-lake-structure.png` - Directory listing
- `demos/screenshots/04-fraud-detection-code.png` - Key fraud detection logic

---

### Part 3: Workflow Orchestration with Airflow (2 minutes)

**Script**:
> "All these pipelines are orchestrated by Apache Airflow. Let me show you the DAGs."

**Steps to demonstrate**:

1. **Open Airflow UI**
   - Navigate to http://localhost:8082
   - Login: admin / airflow_pwd

2. **Show DAG Graph Views**
   - Click on `data_ingestion_pipeline`
   - Show the Graph view
   - Explain: Kafka health check → Schema Registry check → Seed transactions

3. **Show DAG Runs**
   - Click on `dbt_orchestration`
   - Show Grid view with successful runs
   - Click into a task to show logs

4. **Show ML Pipeline DAG**
   - Open `ml_pipeline_orchestration`
   - Explain the weekly schedule
   - Show dependencies on dbt completion

5. **Trigger a DAG manually**
   ```bash
   airflow dags trigger data_ingestion_pipeline --conf '{"num_transactions": 100}'
   ```
   - Watch it run in the UI

**Screenshot locations**:
- `demos/screenshots/05-airflow-dags-list.png` - Main DAGs page
- `demos/screenshots/06-data-ingestion-dag-graph.png` - Graph view
- `demos/screenshots/07-dbt-dag-graph.png` - dbt orchestration DAG
- `demos/screenshots/08-ml-pipeline-dag-graph.png` - ML pipeline DAG
- `demos/screenshots/09-dag-run-success.png` - Successful DAG run

---

### Part 4: ML Training & Experiment Tracking (2 minutes)

**Script**:
> "The platform includes an ML pipeline for fraud detection. Models are tracked using MLflow."

**Steps to demonstrate**:

1. **Open MLflow UI**
   - Navigate to http://localhost:5002
   - Show experiments list

2. **Show Experiment Runs**
   - Click into "fraud-detection" experiment
   - Show multiple runs with different models
   - Compare metrics (precision, recall, F1 score)

3. **Show Run Details**
   - Click on a specific run
   - Show parameters, metrics, and artifacts
   - Show model artifacts

4. **Show Model Registry**
   - Navigate to Models tab
   - Show registered "fraud-detection-model"
   - Show version history

5. **Run Training Script**
   ```bash
   cd ml-platform/training
   python fraud_detection_trainer.py
   ```
   - Show the training output
   - Show new run appearing in MLflow UI

**Screenshot locations**:
- `demos/screenshots/10-mlflow-experiments.png` - Experiments list
- `demos/screenshots/11-mlflow-run-comparison.png` - Comparing runs
- `demos/screenshots/12-mlflow-run-details.png` - Individual run details
- `demos/screenshots/13-mlflow-model-registry.png` - Model registry

---

### Part 5: Monitoring with Grafana (1 minute)

**Script**:
> "Platform health is monitored using Prometheus and visualized in Grafana."

**Steps to demonstrate**:

1. **Open Grafana**
   - Navigate to http://localhost:3002
   - Login: admin / admin

2. **Show Dashboards** (if configured)
   - Show system metrics dashboard
   - Point out key metrics:
     - Kafka throughput
     - Spark processing rate
     - ML model predictions per second

3. **Show Prometheus Data Source**
   - Go to Configuration → Data Sources
   - Show Prometheus is connected

**Screenshot locations**:
- `demos/screenshots/14-grafana-dashboard.png` - Main dashboard
- `demos/screenshots/15-prometheus-metrics.png` - Prometheus targets page

---

### Part 6: Code Quality & Documentation (30 seconds)

**Script**:
> "The codebase follows best practices with pre-commit hooks, comprehensive tests, and documentation."

**Steps to demonstrate**:

1. **Show Project Structure**
   ```bash
   tree -L 2 -I 'node_modules|__pycache__|*.pyc'
   ```

2. **Show Documentation**
   - Open `data-platform/processing/README.md`
   - Open `data-platform/orchestration/dags/README.md`
   - Open `ml-platform/training/README.md`

3. **Show Pre-commit Configuration**
   ```bash
   cat .pre-commit-config.yaml
   ```

**Screenshot locations**:
- `demos/screenshots/16-project-structure.png` - Directory tree
- `demos/screenshots/17-documentation.png` - README preview

---

### Conclusion (30 seconds)

**Script**:
> "This platform demonstrates my expertise in building production-ready data pipelines with real-time processing, ML integration, and proper orchestration. The code is available on GitHub, and I'd be happy to discuss any aspects of the implementation. Thank you!"

**What to show**:
- GitHub repository: https://github.com/KrishnaSathvik/data-platform-portfolio
- Final architecture diagram

---

## Screenshot Checklist

Create these screenshots for your portfolio:

### Airflow Screenshots
- [ ] `05-airflow-dags-list.png` - All DAGs overview
- [ ] `06-data-ingestion-dag-graph.png` - Data ingestion workflow
- [ ] `07-dbt-dag-graph.png` - dbt transformation workflow
- [ ] `08-ml-pipeline-dag-graph.png` - ML training workflow
- [ ] `09-dag-run-success.png` - Successful task execution

### MLflow Screenshots
- [ ] `10-mlflow-experiments.png` - Experiment tracking
- [ ] `11-mlflow-run-comparison.png` - Model comparison
- [ ] `12-mlflow-run-details.png` - Run details with metrics
- [ ] `13-mlflow-model-registry.png` - Registered models

### Infrastructure Screenshots
- [ ] `01-kafka-producer.png` - Transaction generation
- [ ] `02-kafka-messages.png` - Kafka messages
- [ ] `03-delta-lake-structure.png` - Delta Lake medallion layers
- [ ] `04-fraud-detection-code.png` - Code highlight
- [ ] `14-grafana-dashboard.png` - Monitoring dashboard
- [ ] `15-prometheus-metrics.png` - Metrics collection
- [ ] `16-project-structure.png` - Repository structure
- [ ] `17-documentation.png` - Documentation example

---

## Video Recording Tips

### Tools
- **macOS**: QuickTime Player (File → New Screen Recording)
- **Windows**: OBS Studio (free)
- **Linux**: SimpleScreenRecorder

### Recording Settings
- **Resolution**: 1920x1080 (1080p)
- **Frame Rate**: 30 FPS
- **Format**: MP4 (H.264)
- **Audio**: Record your voice explaining each step

### Best Practices
1. **Clean workspace**: Close unnecessary tabs and applications
2. **Practice**: Run through the demo 2-3 times before recording
3. **Pace**: Speak slowly and clearly
4. **Zoom**: Zoom in on important code sections
5. **Transitions**: Use smooth transitions between topics
6. **Editing**: Edit out mistakes, pauses, and errors

### Video Editing (Optional)
- **iMovie** (macOS) - Free, simple
- **DaVinci Resolve** (All platforms) - Free, professional
- Add:
  - Title slides for each section
  - Annotations highlighting key points
  - Background music (low volume)
  - Closing slide with contact info

---

## Publishing Your Demo

### YouTube Upload
1. Create unlisted/public video
2. Title: "End-to-End Data Platform: Real-time Processing, ML, & Orchestration"
3. Description: Include GitHub link, tech stack, timestamps
4. Tags: data engineering, apache kafka, spark, airflow, mlflow, python

### Portfolio Website
- Embed YouTube video
- Add screenshot gallery
- Link to GitHub repository
- Include tech stack badges

### LinkedIn Post
```
🚀 Just completed my Data Platform Portfolio Project!

Built an end-to-end platform featuring:
✅ Real-time streaming (Kafka → Spark → Delta Lake)
✅ ML pipeline (Fraud detection with MLflow)
✅ Orchestration (Apache Airflow)
✅ Monitoring (Prometheus + Grafana)

Tech stack: Python, Spark, Kafka, Airflow, MLflow, dbt, PostgreSQL, Docker

Watch the demo 👇
[Video Link]

Code on GitHub 👇
[Repo Link]

#DataEngineering #MachineLearning #ApacheSpark #Python
```

---

## Common Issues & Solutions

### Issue: Services not running
```bash
# Check Docker
docker ps
# Restart services
cd infra/docker && docker compose up -d
```

### Issue: Airflow DAGs not visible
```bash
# Refresh DAGs
docker exec airflow-webserver airflow dags list-import-errors
# Restart Airflow
docker restart airflow-webserver
```

### Issue: MLflow experiments not showing
```bash
# Check MLflow
curl http://localhost:5002/health
# Restart MLflow
docker restart mlflow
```

### Issue: Screen recording laggy
- Reduce recording resolution to 720p
- Close all other applications
- Use hardware encoding if available

---

## Portfolio Enhancement Ideas

1. **Create GIFs**: Convert key demo moments into GIFs for README
2. **Add badges**: GitHub shields for tech stack
3. **Blog post**: Write detailed technical blog post
4. **Slides**: Create presentation deck for interviews
5. **Metrics**: Add performance benchmarks to README
