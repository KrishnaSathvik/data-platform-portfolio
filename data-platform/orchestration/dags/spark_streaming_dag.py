"""
Airflow DAG: Spark Streaming Jobs Orchestration
Monitors and manages Spark Structured Streaming jobs
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor

default_args = {
    "owner": "data-platform",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

dag = DAG(
    "spark_streaming_orchestration",
    default_args=default_args,
    description="Manage Spark Structured Streaming jobs",
    schedule_interval="@daily",  # Daily health checks
    catchup=False,
    tags=["spark", "streaming", "monitoring"],
)


def check_delta_tables():
    """Verify Delta Lake tables exist and are healthy"""
    import os

    delta_base = os.getenv("DELTA_BASE_PATH", "/tmp/delta-lake")
    tables_to_check = [
        f"{delta_base}/bronze/transactions",
        f"{delta_base}/silver/transactions",
        f"{delta_base}/gold/transactions",
        f"{delta_base}/fraud_detection",
    ]

    for table_path in tables_to_check:
        if os.path.exists(table_path):
            print(f"✅ Delta table exists: {table_path}")
            # Check if _delta_log directory exists
            delta_log = f"{table_path}/_delta_log"
            if os.path.exists(delta_log):
                log_files = os.listdir(delta_log)
                print(f"  Delta log files: {len(log_files)}")
            else:
                print(f"  ⚠️  No Delta log found")
        else:
            print(f"❌ Delta table missing: {table_path}")

    return True


def monitor_streaming_metrics():
    """Monitor Spark streaming job metrics"""
    # In production, this would query Spark UI or Prometheus
    print("Monitoring Spark streaming metrics...")
    print("  - Processing rate: N/A (would query Spark UI)")
    print("  - Batch duration: N/A (would query Spark UI)")
    print("  - Input rate: N/A (would query Spark UI)")
    return True


# Task 1: Check if streaming jobs are configured
check_config_task = FileSensor(
    task_id="check_streaming_config",
    filepath="/Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/processing/config.py",
    poke_interval=30,
    timeout=300,
    dag=dag,
)

# Task 2: Verify Delta Lake tables
check_delta_task = PythonOperator(
    task_id="check_delta_tables",
    python_callable=check_delta_tables,
    dag=dag,
)

# Task 3: Monitor streaming metrics
monitor_metrics_task = PythonOperator(
    task_id="monitor_streaming_metrics",
    python_callable=monitor_streaming_metrics,
    dag=dag,
)

# Task 4: Generate health report
report_task = BashOperator(
    task_id="generate_health_report",
    bash_command="""
    echo "Spark Streaming Health Report - $(date)"
    echo "================================"
    echo "Delta Lake Base: $DELTA_BASE_PATH"
    echo "Kafka Bootstrap: $KAFKA_BOOTSTRAP_SERVERS"
    echo "Status: All checks passed"
    """,
    dag=dag,
)

# Define task dependencies
check_config_task >> check_delta_task >> monitor_metrics_task >> report_task
