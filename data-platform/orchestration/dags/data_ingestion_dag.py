"""
Airflow DAG: Data Ingestion Pipeline
Orchestrates Kafka data generation and monitoring
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "data_ingestion_pipeline",
    default_args=default_args,
    description="Ingest e-commerce transaction data into Kafka",
    schedule_interval="@hourly",
    catchup=False,
    tags=["ingestion", "kafka", "ecommerce"],
)


def check_kafka_health():
    """Check if Kafka cluster is healthy"""
    import os

    from kafka import KafkaAdminClient
    from kafka.errors import KafkaError

    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers, client_id="airflow-health-check"
        )
        # Get cluster metadata
        metadata = admin_client._client.cluster
        print(f"Kafka cluster is healthy. Brokers: {len(metadata.brokers())}")
        admin_client.close()
        return True
    except KafkaError as e:
        print(f"Kafka health check failed: {str(e)}")
        raise


def seed_transactions(**context):
    """Generate and send transaction events to Kafka"""
    import os
    import sys

    # Add ingestion directory to path
    sys.path.append(
        "/Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/ingestion"
    )

    from seed_events import generate_transactions, send_to_kafka

    # Generate 1000 transactions per run
    num_transactions = context["dag_run"].conf.get("num_transactions", 1000)

    print(f"Generating {num_transactions} transaction events...")

    transactions = generate_transactions(num_transactions)
    send_to_kafka(transactions)

    print(f"Successfully sent {num_transactions} transactions to Kafka")


def check_schema_registry():
    """Verify Schema Registry is accessible"""
    import os

    import requests

    schema_registry_url = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")

    try:
        response = requests.get(f"{schema_registry_url}/subjects")
        response.raise_for_status()
        subjects = response.json()
        print(f"Schema Registry is healthy. Subjects: {subjects}")
        return True
    except Exception as e:
        print(f"Schema Registry check failed: {str(e)}")
        raise


# Task 1: Check Kafka health
check_kafka_task = PythonOperator(
    task_id="check_kafka_health",
    python_callable=check_kafka_health,
    dag=dag,
)

# Task 2: Check Schema Registry
check_schema_task = PythonOperator(
    task_id="check_schema_registry",
    python_callable=check_schema_registry,
    dag=dag,
)

# Task 3: Seed transactions to Kafka
seed_task = PythonOperator(
    task_id="seed_transactions",
    python_callable=seed_transactions,
    provide_context=True,
    dag=dag,
)

# Task 4: Verify data in Kafka topic
verify_kafka_task = BashOperator(
    task_id="verify_kafka_topic",
    bash_command="""
    docker exec kafka kafka-topics --bootstrap-server localhost:9092 \
        --describe --topic ecommerce.transactions
    """,
    dag=dag,
)

# Define task dependencies
check_kafka_task >> check_schema_task >> seed_task >> verify_kafka_task
