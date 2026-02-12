"""
Airflow DAG: ML Pipeline Orchestration
Trains, evaluates, and deploys ML models
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

default_args = {
    "owner": "ml-platform",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "ml_pipeline_orchestration",
    default_args=default_args,
    description="Train and deploy fraud detection ML models",
    schedule_interval="0 0 * * 0",  # Weekly on Sunday
    catchup=False,
    tags=["ml", "mlflow", "fraud-detection"],
)


def check_mlflow_connection():
    """Verify MLflow tracking server is accessible"""
    import os

    import mlflow

    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5002")
    mlflow.set_tracking_uri(mlflow_uri)

    try:
        # Try to get experiments
        experiments = mlflow.search_experiments()
        print(f"MLflow connection successful. Found {len(experiments)} experiments")
        return True
    except Exception as e:
        print(f"MLflow connection failed: {str(e)}")
        raise


def extract_training_data():
    """Extract training data from Delta Lake"""
    import os

    import pandas as pd

    delta_path = os.getenv("DELTA_BASE_PATH", "/tmp/delta-lake")
    fraud_detection_path = f"{delta_path}/fraud_detection"

    print(f"Extracting training data from: {fraud_detection_path}")

    try:
        # Read from Delta Lake (simplified - in production use Spark)
        # For this demo, we'll create sample data
        import numpy as np

        np.random.seed(42)
        n_samples = 10000

        data = {
            "amount": np.random.exponential(100, n_samples),
            "transaction_hour": np.random.randint(0, 24, n_samples),
            "is_weekend": np.random.choice([0, 1], n_samples),
            "fraud_score": np.random.randint(0, 100, n_samples),
            "is_fraud": np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        }

        df = pd.DataFrame(data)
        output_path = "/tmp/training_data.csv"
        df.to_csv(output_path, index=False)

        print(f"Training data extracted: {len(df)} records")
        print(f"Fraud rate: {df['is_fraud'].mean():.2%}")

        return output_path

    except Exception as e:
        print(f"Failed to extract training data: {str(e)}")
        raise


def train_fraud_model(**context):
    """Train fraud detection model and log to MLflow"""
    import os

    import mlflow
    import mlflow.sklearn
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import (
        accuracy_score,
        f1_score,
        precision_score,
        recall_score,
        roc_auc_score,
    )
    from sklearn.model_selection import train_test_split

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5002"))
    mlflow.set_experiment("fraud-detection")

    # Load training data
    data_path = context["task_instance"].xcom_pull(task_ids="extract_training_data")
    df = pd.read_csv(data_path)

    # Prepare features and target
    feature_cols = ["amount", "transaction_hour", "is_weekend", "fraud_score"]
    X = df[feature_cols]
    y = df["is_fraud"]

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Start MLflow run
    with mlflow.start_run(
        run_name=f"fraud_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    ):

        # Log parameters
        params = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "random_state": 42,
        }
        mlflow.log_params(params)

        # Train model
        print("Training Random Forest model...")
        model = RandomForestClassifier(**params)
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_pred_proba),
        }

        # Log metrics
        mlflow.log_metrics(metrics)

        # Log model
        mlflow.sklearn.log_model(model, "model")

        # Log feature importance
        feature_importance = pd.DataFrame(
            {"feature": feature_cols, "importance": model.feature_importances_}
        ).sort_values("importance", ascending=False)

        mlflow.log_dict(feature_importance.to_dict(), "feature_importance.json")

        print(f"Model trained successfully!")
        print(f"Metrics: {metrics}")

        return mlflow.active_run().info.run_id


def evaluate_model(**context):
    """Evaluate model performance and decide if it should be deployed"""
    run_id = context["task_instance"].xcom_pull(task_ids="train_fraud_model")

    import mlflow

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5002"))

    # Get run metrics
    run = mlflow.get_run(run_id)
    metrics = run.data.metrics

    print(f"Model Evaluation Results:")
    print(f"  Accuracy: {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall: {metrics['recall']:.4f}")
    print(f"  F1 Score: {metrics['f1_score']:.4f}")
    print(f"  ROC-AUC: {metrics['roc_auc']:.4f}")

    # Deployment criteria
    min_precision = 0.80
    min_recall = 0.70
    min_f1 = 0.75

    deploy = (
        metrics["precision"] >= min_precision
        and metrics["recall"] >= min_recall
        and metrics["f1_score"] >= min_f1
    )

    if deploy:
        print("✅ Model meets deployment criteria")
        # Register model
        model_uri = f"runs:/{run_id}/model"
        mlflow.register_model(model_uri, "fraud-detection-model")
    else:
        print("❌ Model does not meet deployment criteria")

    return deploy


# Task 1: Check MLflow connection
check_mlflow_task = PythonOperator(
    task_id="check_mlflow_connection",
    python_callable=check_mlflow_connection,
    dag=dag,
)

# Task 2: Wait for dbt pipeline to complete
wait_for_dbt = ExternalTaskSensor(
    task_id="wait_for_dbt_pipeline",
    external_dag_id="dbt_orchestration",
    external_task_id="dbt_run_marts",
    timeout=3600,
    allowed_states=["success"],
    failed_states=["failed", "skipped"],
    mode="reschedule",
    dag=dag,
)

# Task 3: Extract training data
extract_data_task = PythonOperator(
    task_id="extract_training_data",
    python_callable=extract_training_data,
    dag=dag,
)

# Task 4: Train fraud detection model
train_model_task = PythonOperator(
    task_id="train_fraud_model",
    python_callable=train_fraud_model,
    provide_context=True,
    dag=dag,
)

# Task 5: Evaluate model
evaluate_task = PythonOperator(
    task_id="evaluate_model",
    python_callable=evaluate_model,
    provide_context=True,
    dag=dag,
)

# Task 6: Deploy model (if evaluation passes)
deploy_task = BashOperator(
    task_id="deploy_model",
    bash_command='echo "Deploying model to production..."',
    dag=dag,
)

# Define task dependencies
check_mlflow_task >> wait_for_dbt >> extract_data_task
extract_data_task >> train_model_task >> evaluate_task >> deploy_task
