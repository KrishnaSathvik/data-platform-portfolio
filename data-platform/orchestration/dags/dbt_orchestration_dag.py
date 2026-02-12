"""
Airflow DAG: dbt Orchestration
Runs dbt models to transform data in the warehouse
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "data-platform",
    "depends_on_past": True,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=3),
}

dag = DAG(
    "dbt_orchestration",
    default_args=default_args,
    description="Run dbt models to transform warehouse data",
    schedule_interval="0 */6 * * *",  # Every 6 hours
    catchup=False,
    tags=["dbt", "warehouse", "transformation"],
)


def check_postgres_connection():
    """Verify PostgreSQL warehouse is accessible"""
    import os

    import psycopg2

    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="warehouse",
            user="postgres",
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL connection successful: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"PostgreSQL connection failed: {str(e)}")
        raise


# Task 1: Check database connection
check_db_task = PythonOperator(
    task_id="check_postgres_connection",
    python_callable=check_postgres_connection,
    dag=dag,
)

# Task 2: dbt deps (install dependencies)
dbt_deps_task = BashOperator(
    task_id="dbt_deps",
    bash_command="cd /Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/warehouse && dbt deps",
    dag=dag,
)

# Task 3: dbt seed (load seed data)
dbt_seed_task = BashOperator(
    task_id="dbt_seed",
    bash_command="cd /Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/warehouse && dbt seed",
    dag=dag,
)

# Task 4: dbt run staging models
dbt_run_staging_task = BashOperator(
    task_id="dbt_run_staging",
    bash_command="cd /Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/warehouse && dbt run --select staging.*",
    dag=dag,
)

# Task 5: dbt run marts models
dbt_run_marts_task = BashOperator(
    task_id="dbt_run_marts",
    bash_command="cd /Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/warehouse && dbt run --select marts.*",
    dag=dag,
)

# Task 6: dbt test
dbt_test_task = BashOperator(
    task_id="dbt_test",
    bash_command="cd /Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/warehouse && dbt test",
    dag=dag,
)

# Task 7: dbt docs generate
dbt_docs_task = BashOperator(
    task_id="dbt_docs_generate",
    bash_command="cd /Users/krishnasathvikmantripragada/data-platform-portfolio/data-platform/warehouse && dbt docs generate",
    dag=dag,
)

# Define task dependencies
check_db_task >> dbt_deps_task >> dbt_seed_task
dbt_seed_task >> dbt_run_staging_task >> dbt_run_marts_task
dbt_run_marts_task >> dbt_test_task >> dbt_docs_task
