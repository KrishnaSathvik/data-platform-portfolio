"""
Fraud Detection Model Training
Train ML models to detect fraudulent transactions
"""

import os
from datetime import datetime

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler


class FraudDetectionTrainer:
    """
    Trains and evaluates fraud detection models
    """

    def __init__(self, mlflow_tracking_uri="http://localhost:5002"):
        """
        Initialize trainer

        Args:
            mlflow_tracking_uri: MLflow tracking server URI
        """
        self.mlflow_tracking_uri = mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment("fraud-detection")

        self.scaler = StandardScaler()
        self.models = {}
        self.best_model = None
        self.best_score = 0

    def load_data(self, data_path=None):
        """
        Load training data from CSV or generate sample data

        Args:
            data_path: Path to training data CSV

        Returns:
            X, y: Features and target
        """
        if data_path and os.path.exists(data_path):
            print(f"Loading data from: {data_path}")
            df = pd.read_csv(data_path)
        else:
            print("Generating sample training data...")
            df = self._generate_sample_data()

        # Prepare features and target
        feature_cols = [col for col in df.columns if col != "is_fraud"]
        X = df[feature_cols]
        y = df["is_fraud"]

        print(f"Data loaded: {len(df)} samples")
        print(f"Features: {list(X.columns)}")
        print(f"Fraud rate: {y.mean():.2%}")

        return X, y

    def _generate_sample_data(self, n_samples=10000):
        """Generate synthetic training data"""
        np.random.seed(42)

        # Generate realistic transaction data
        amount = np.random.exponential(100, n_samples)
        transaction_hour = np.random.randint(0, 24, n_samples)
        is_weekend = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        is_high_value = (amount > 1000).astype(int)

        # Create fraud score (simulated)
        fraud_score = (
            (amount > 1000) * 30
            + ((transaction_hour >= 23) | (transaction_hour <= 5)) * 10
            + is_weekend * 5
            + np.random.normal(0, 10, n_samples)
        )

        # Generate fraud labels (5% fraud rate)
        is_fraud = (fraud_score > 40).astype(int)

        # Add some additional features
        payment_method_code = np.random.choice(
            [0, 1, 2, 3], n_samples
        )  # credit, debit, crypto, bank
        user_tx_count = np.random.poisson(10, n_samples)
        device_age_days = np.random.exponential(180, n_samples)

        df = pd.DataFrame(
            {
                "amount": amount,
                "transaction_hour": transaction_hour,
                "is_weekend": is_weekend,
                "is_high_value": is_high_value,
                "fraud_score": fraud_score,
                "payment_method_code": payment_method_code,
                "user_tx_count": user_tx_count,
                "device_age_days": device_age_days,
                "is_fraud": is_fraud,
            }
        )

        return df

    def prepare_data(self, X, y, test_size=0.2):
        """
        Split and scale data

        Args:
            X: Features
            y: Target
            test_size: Test set proportion

        Returns:
            X_train, X_test, y_train, y_test
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")

        return X_train_scaled, X_test_scaled, y_train, y_test

    def train_logistic_regression(self, X_train, y_train):
        """Train Logistic Regression model"""
        print("\nTraining Logistic Regression...")

        with mlflow.start_run(
            run_name=f"logistic_regression_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):

            params = {"C": 1.0, "max_iter": 1000, "random_state": 42}
            mlflow.log_params(params)

            model = LogisticRegression(**params)
            model.fit(X_train, y_train)

            self.models["logistic_regression"] = model

            # Log model
            mlflow.sklearn.log_model(model, "model")

            return model

    def train_random_forest(self, X_train, y_train):
        """Train Random Forest model"""
        print("\nTraining Random Forest...")

        with mlflow.start_run(
            run_name=f"random_forest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):

            params = {
                "n_estimators": 100,
                "max_depth": 10,
                "min_samples_split": 5,
                "random_state": 42,
                "n_jobs": -1,
            }
            mlflow.log_params(params)

            model = RandomForestClassifier(**params)
            model.fit(X_train, y_train)

            self.models["random_forest"] = model

            # Log model
            mlflow.sklearn.log_model(model, "model")

            return model

    def train_gradient_boosting(self, X_train, y_train):
        """Train Gradient Boosting model"""
        print("\nTraining Gradient Boosting...")

        with mlflow.start_run(
            run_name=f"gradient_boosting_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):

            params = {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 5,
                "random_state": 42,
            }
            mlflow.log_params(params)

            model = GradientBoostingClassifier(**params)
            model.fit(X_train, y_train)

            self.models["gradient_boosting"] = model

            # Log model
            mlflow.sklearn.log_model(model, "model")

            return model

    def evaluate_model(self, model, X_test, y_test, model_name):
        """
        Evaluate model and log metrics

        Args:
            model: Trained model
            X_test: Test features
            y_test: Test target
            model_name: Name of the model

        Returns:
            dict: Evaluation metrics
        """
        print(f"\nEvaluating {model_name}...")

        # Make predictions
        y_pred = model.predict(X_test)
        y_pred_proba = (
            model.predict_proba(X_test)[:, 1]
            if hasattr(model, "predict_proba")
            else y_pred
        )

        # Calculate metrics
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_pred_proba),
        }

        # Log metrics to MLflow
        with mlflow.start_run(nested=True):
            mlflow.log_metrics(metrics)

        # Print results
        print(f"Results for {model_name}:")
        for metric_name, value in metrics.items():
            print(f"  {metric_name}: {value:.4f}")

        # Print confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(cm)

        # Print classification report
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred))

        # Track best model
        if metrics["f1_score"] > self.best_score:
            self.best_score = metrics["f1_score"]
            self.best_model = (model_name, model)
            print(f"✅ New best model: {model_name} (F1: {metrics['f1_score']:.4f})")

        return metrics

    def save_model(self, model, model_name, output_dir="./models"):
        """Save model to disk"""
        os.makedirs(output_dir, exist_ok=True)
        model_path = os.path.join(output_dir, f"{model_name}.joblib")
        joblib.dump(model, model_path)
        print(f"Model saved to: {model_path}")

    def train_all_models(self, data_path=None):
        """
        Train and evaluate all models

        Args:
            data_path: Path to training data
        """
        print("=" * 80)
        print("Fraud Detection Model Training Pipeline")
        print("=" * 80)

        # Load data
        X, y = self.load_data(data_path)

        # Prepare data
        X_train, X_test, y_train, y_test = self.prepare_data(X, y)

        # Train models
        lr_model = self.train_logistic_regression(X_train, y_train)
        rf_model = self.train_random_forest(X_train, y_train)
        gb_model = self.train_gradient_boosting(X_train, y_train)

        # Evaluate all models
        lr_metrics = self.evaluate_model(
            lr_model, X_test, y_test, "Logistic Regression"
        )
        rf_metrics = self.evaluate_model(rf_model, X_test, y_test, "Random Forest")
        gb_metrics = self.evaluate_model(gb_model, X_test, y_test, "Gradient Boosting")

        # Print best model
        print("\n" + "=" * 80)
        print(f"🏆 Best Model: {self.best_model[0]}")
        print(f"   F1 Score: {self.best_score:.4f}")
        print("=" * 80)

        # Save best model
        self.save_model(self.best_model[1], self.best_model[0])

        # Save scaler
        scaler_path = "./models/scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        print(f"Scaler saved to: {scaler_path}")

        return {
            "logistic_regression": lr_metrics,
            "random_forest": rf_metrics,
            "gradient_boosting": gb_metrics,
            "best_model": self.best_model[0],
        }


if __name__ == "__main__":
    # Initialize trainer
    trainer = FraudDetectionTrainer()

    # Train all models
    results = trainer.train_all_models()

    print("\n✅ Training pipeline completed successfully!")
