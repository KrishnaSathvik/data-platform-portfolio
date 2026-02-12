"""
Hyperparameter Tuning for Fraud Detection Models
Uses GridSearchCV and RandomizedSearchCV for optimization
"""

from datetime import datetime

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from fraud_detection_trainer import FraudDetectionTrainer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import f1_score, make_scorer
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, StratifiedKFold


class HyperparameterTuner:
    """
    Hyperparameter tuning for fraud detection models
    """

    def __init__(self, mlflow_tracking_uri="http://localhost:5002"):
        """Initialize tuner"""
        self.mlflow_tracking_uri = mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment("fraud-detection-tuning")

        self.trainer = FraudDetectionTrainer(mlflow_tracking_uri)

    def tune_random_forest(self, X_train, y_train):
        """
        Tune Random Forest hyperparameters using GridSearchCV

        Args:
            X_train: Training features
            y_train: Training target

        Returns:
            best_estimator: Best model found
        """
        print("\n" + "=" * 80)
        print("Tuning Random Forest Hyperparameters (GridSearchCV)")
        print("=" * 80)

        # Define parameter grid
        param_grid = {
            "n_estimators": [50, 100, 200],
            "max_depth": [5, 10, 15, None],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
            "max_features": ["sqrt", "log2"],
        }

        # Setup cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Create scorer (F1 score for imbalanced data)
        scorer = make_scorer(f1_score)

        # Initialize GridSearchCV
        rf = RandomForestClassifier(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            estimator=rf,
            param_grid=param_grid,
            scoring=scorer,
            cv=cv,
            n_jobs=-1,
            verbose=2,
        )

        with mlflow.start_run(
            run_name=f"rf_grid_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):
            # Fit grid search
            grid_search.fit(X_train, y_train)

            # Log best parameters
            print(f"\nBest Parameters: {grid_search.best_params_}")
            print(f"Best CV Score: {grid_search.best_score_:.4f}")

            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric("best_cv_score", grid_search.best_score_)

            # Log all CV results
            cv_results = pd.DataFrame(grid_search.cv_results_)
            mlflow.log_dict(cv_results.to_dict(), "cv_results.json")

            # Log best model
            mlflow.sklearn.log_model(grid_search.best_estimator_, "model")

        return grid_search.best_estimator_

    def tune_gradient_boosting(self, X_train, y_train):
        """
        Tune Gradient Boosting hyperparameters using RandomizedSearchCV

        Args:
            X_train: Training features
            y_train: Training target

        Returns:
            best_estimator: Best model found
        """
        print("\n" + "=" * 80)
        print("Tuning Gradient Boosting Hyperparameters (RandomizedSearchCV)")
        print("=" * 80)

        # Define parameter distributions for random search
        param_distributions = {
            "n_estimators": [50, 100, 150, 200, 250],
            "learning_rate": [0.01, 0.05, 0.1, 0.15, 0.2],
            "max_depth": [3, 4, 5, 6, 7],
            "min_samples_split": [2, 5, 10, 15],
            "min_samples_leaf": [1, 2, 4, 6],
            "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
            "max_features": ["sqrt", "log2", None],
        }

        # Setup cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

        # Create scorer
        scorer = make_scorer(f1_score)

        # Initialize RandomizedSearchCV
        gb = GradientBoostingClassifier(random_state=42)
        random_search = RandomizedSearchCV(
            estimator=gb,
            param_distributions=param_distributions,
            n_iter=50,  # Number of parameter settings sampled
            scoring=scorer,
            cv=cv,
            n_jobs=-1,
            verbose=2,
            random_state=42,
        )

        with mlflow.start_run(
            run_name=f"gb_random_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        ):
            # Fit random search
            random_search.fit(X_train, y_train)

            # Log best parameters
            print(f"\nBest Parameters: {random_search.best_params_}")
            print(f"Best CV Score: {random_search.best_score_:.4f}")

            mlflow.log_params(random_search.best_params_)
            mlflow.log_metric("best_cv_score", random_search.best_score_)

            # Log all CV results
            cv_results = pd.DataFrame(random_search.cv_results_)
            mlflow.log_dict(cv_results.to_dict(), "cv_results.json")

            # Log best model
            mlflow.sklearn.log_model(random_search.best_estimator_, "model")

        return random_search.best_estimator_

    def tune_all_models(self, data_path=None):
        """
        Run hyperparameter tuning for all models

        Args:
            data_path: Path to training data
        """
        print("=" * 80)
        print("Hyperparameter Tuning Pipeline")
        print("=" * 80)

        # Load and prepare data
        X, y = self.trainer.load_data(data_path)
        X_train, X_test, y_train, y_test = self.trainer.prepare_data(X, y)

        # Tune Random Forest
        best_rf = self.tune_random_forest(X_train, y_train)

        # Tune Gradient Boosting
        best_gb = self.tune_gradient_boosting(X_train, y_train)

        # Evaluate tuned models
        print("\n" + "=" * 80)
        print("Evaluating Tuned Models")
        print("=" * 80)

        rf_metrics = self.trainer.evaluate_model(
            best_rf, X_test, y_test, "Tuned Random Forest"
        )
        gb_metrics = self.trainer.evaluate_model(
            best_gb, X_test, y_test, "Tuned Gradient Boosting"
        )

        # Compare results
        print("\n" + "=" * 80)
        print("Tuning Results Comparison")
        print("=" * 80)
        print(f"\nTuned Random Forest F1 Score: {rf_metrics['f1_score']:.4f}")
        print(f"Tuned Gradient Boosting F1 Score: {gb_metrics['f1_score']:.4f}")

        # Determine best overall model
        if rf_metrics["f1_score"] > gb_metrics["f1_score"]:
            best_model = ("Tuned Random Forest", best_rf, rf_metrics)
        else:
            best_model = ("Tuned Gradient Boosting", best_gb, gb_metrics)

        print(f"\n🏆 Best Tuned Model: {best_model[0]}")
        print(f"   F1 Score: {best_model[2]['f1_score']:.4f}")

        # Save best model
        self.trainer.save_model(
            best_model[1], f"{best_model[0].lower().replace(' ', '_')}_tuned"
        )

        print("\n✅ Hyperparameter tuning completed!")

        return {
            "random_forest": rf_metrics,
            "gradient_boosting": gb_metrics,
            "best_model": best_model[0],
        }


if __name__ == "__main__":
    # Initialize tuner
    tuner = HyperparameterTuner()

    # Run tuning
    results = tuner.tune_all_models()

    print("\n✅ Hyperparameter tuning pipeline completed successfully!")
