# Airflow DAGs

This directory contains Airflow DAGs for orchestrating the data platform.

## DAGs Overview

### 1. `data_ingestion_dag.py`
**Purpose**: Ingest e-commerce transaction data into Kafka

**Schedule**: Hourly (`@hourly`)

**Tasks**:
1. Check Kafka health
2. Check Schema Registry
3. Seed transactions to Kafka
4. Verify Kafka topic

**Dependencies**: None

**Trigger manually with custom parameters**:
```bash
airflow dags trigger data_ingestion_pipeline \
    --conf '{"num_transactions": 5000}'
```

---

### 2. `dbt_orchestration_dag.py`
**Purpose**: Run dbt models to transform warehouse data

**Schedule**: Every 6 hours (`0 */6 * * *`)

**Tasks**:
1. Check PostgreSQL connection
2. Install dbt dependencies (`dbt deps`)
3. Load seed data (`dbt seed`)
4. Run staging models
5. Run marts models
6. Run dbt tests
7. Generate dbt docs

**Dependencies**: Depends on data being available in warehouse

**Manual trigger**:
```bash
airflow dags trigger dbt_orchestration
```

---

### 3. `ml_pipeline_dag.py`
**Purpose**: Train and deploy fraud detection ML models

**Schedule**: Weekly on Sunday (`0 0 * * 0`)

**Tasks**:
1. Check MLflow connection
2. Wait for dbt pipeline completion
3. Extract training data from Delta Lake
4. Train fraud detection model (Random Forest)
5. Evaluate model performance
6. Deploy model (if meets criteria)

**Model Deployment Criteria**:
- Precision ≥ 80%
- Recall ≥ 70%
- F1 Score ≥ 75%

**Dependencies**: Requires `dbt_orchestration` DAG to complete

**Manual trigger**:
```bash
airflow dags trigger ml_pipeline_orchestration
```

---

### 4. `spark_streaming_dag.py`
**Purpose**: Monitor and manage Spark Structured Streaming jobs

**Schedule**: Daily (`@daily`)

**Tasks**:
1. Check streaming configuration exists
2. Verify Delta Lake tables are healthy
3. Monitor streaming metrics
4. Generate health report

**Dependencies**: None (monitoring only)

**Manual trigger**:
```bash
airflow dags trigger spark_streaming_orchestration
```

---

## DAG Dependencies Graph

```
data_ingestion_dag (hourly)
    ↓
Kafka Topics populated
    ↓
[Spark Streaming Jobs run continuously]
    ↓
Delta Lake tables (Bronze/Silver/Gold)
    ↓
dbt_orchestration_dag (every 6 hours)
    ↓
PostgreSQL Warehouse (marts)
    ↓
ml_pipeline_dag (weekly)
    ↓
MLflow Models
```

## Configuration

### Environment Variables
DAGs use these environment variables:
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SCHEMA_REGISTRY_URL=http://localhost:8081
POSTGRES_PASSWORD=postgres
MLFLOW_TRACKING_URI=http://localhost:5002
DELTA_BASE_PATH=/tmp/delta-lake
```

### Airflow Connections
No Airflow Connections required - all configured via environment variables.

### Airflow Variables
Optional variables for customization:
- `data_platform_num_transactions`: Default transactions per ingestion run
- `ml_min_precision`: Minimum precision for model deployment
- `ml_min_recall`: Minimum recall for model deployment

## Usage

### Access Airflow UI
```bash
# Airflow is running in Docker
open http://localhost:8082

# Credentials
Username: admin
Password: admin
```

### Enable/Disable DAGs
```bash
# Enable a DAG
airflow dags unpause data_ingestion_pipeline

# Disable a DAG
airflow dags pause data_ingestion_pipeline
```

### View DAG Status
```bash
# List all DAGs
airflow dags list

# Get DAG state
airflow dags state data_ingestion_pipeline
```

### Trigger DAG Manually
```bash
# Trigger with default config
airflow dags trigger data_ingestion_pipeline

# Trigger with custom config
airflow dags trigger data_ingestion_pipeline \
    --conf '{"num_transactions": 10000}'
```

### View Task Logs
```bash
# View logs for a specific task
airflow tasks logs data_ingestion_pipeline seed_transactions <execution_date>
```

## Monitoring

### Key Metrics to Monitor
1. **DAG Success Rate**: Percentage of successful runs
2. **Task Duration**: How long each task takes
3. **Failure Rate**: Tasks/DAGs that fail frequently
4. **SLA Misses**: Tasks that don't complete within SLA
5. **Queue Length**: Pending tasks in the executor

### Alerting
Configure email or Slack alerts:
```python
# In DAG default_args
'email': ['data-team@company.com'],
'email_on_failure': True,
'email_on_retry': True,
'email_on_success': False,
```

## Best Practices

1. **Idempotency**: All tasks should be idempotent (safe to run multiple times)
2. **Task Granularity**: Break complex operations into smaller tasks
3. **Error Handling**: Use retries and proper error handling
4. **Documentation**: Document DAG purpose and task dependencies
5. **Testing**: Test DAGs locally before deploying
6. **Monitoring**: Set up alerts for critical DAGs
7. **Backfilling**: Use `catchup=False` unless historical backfill is needed

## Troubleshooting

### DAG Not Appearing in UI
- Check DAG file syntax: `python dags/your_dag.py`
- Check Airflow DAG directory: `airflow dags list`
- Refresh DAG list in UI

### Task Failing
1. Check task logs in Airflow UI
2. Verify dependencies are installed
3. Check environment variables
4. Verify external systems (Kafka, PostgreSQL, etc.) are accessible

### Long Task Duration
- Profile the task code
- Check external system performance
- Consider breaking into smaller tasks
- Increase task resources if needed

### SLA Misses
- Adjust SLA thresholds if too aggressive
- Optimize task performance
- Increase Airflow worker resources
- Review task dependencies

## Future Enhancements

- [ ] Add data quality checks
- [ ] Implement SLA monitoring
- [ ] Add PagerDuty/Slack integration
- [ ] Create custom operators for common tasks
- [ ] Add more comprehensive error handling
- [ ] Implement data lineage tracking
- [ ] Add performance metrics dashboard
