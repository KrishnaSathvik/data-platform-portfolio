# ML Training Pipeline

Machine learning model training for fraud detection.

## Overview

This directory contains scripts for training, tuning, and evaluating fraud detection models.

## Components

### 1. `fraud_detection_trainer.py`
Main training script that trains multiple models:

**Models Trained:**
- Logistic Regression (baseline)
- Random Forest (ensemble)
- Gradient Boosting (advanced ensemble)

**Features:**
- Automated data loading and preprocessing
- StandardScaler for feature scaling
- Train/test split with stratification
- Comprehensive evaluation metrics
- MLflow experiment tracking
- Model persistence

**Usage:**
```bash
python fraud_detection_trainer.py
```

**Metrics Tracked:**
- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC
- Confusion Matrix
- Classification Report

### 2. `hyperparameter_tuning.py`
Hyperparameter optimization using grid search and random search:

**Random Forest Tuning (GridSearchCV):**
- n_estimators: [50, 100, 200]
- max_depth: [5, 10, 15, None]
- min_samples_split: [2, 5, 10]
- min_samples_leaf: [1, 2, 4]
- max_features: ['sqrt', 'log2']

**Gradient Boosting Tuning (RandomizedSearchCV):**
- n_estimators: [50-250]
- learning_rate: [0.01-0.2]
- max_depth: [3-7]
- subsample: [0.6-1.0]
- And more...

**Usage:**
```bash
python hyperparameter_tuning.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Training Pipeline

### Step 1: Basic Training
Train all baseline models:
```bash
python fraud_detection_trainer.py
```

### Step 2: Hyperparameter Tuning
Optimize the best performing models:
```bash
python hyperparameter_tuning.py
```

### Step 3: View Results in MLflow
```bash
# MLflow UI is already running in Docker
open http://localhost:5002
```

## Data Requirements

The training scripts can:
1. **Load from file**: Provide path to CSV with these columns:
   - `amount` (float)
   - `transaction_hour` (int, 0-23)
   - `is_weekend` (bool/int)
   - `fraud_score` (float)
   - `is_fraud` (bool/int) - target variable

2. **Generate synthetic data**: If no file provided, generates 10,000 samples

## Model Evaluation

Models are evaluated using:

### Primary Metrics
- **F1 Score**: Balance between precision and recall
- **ROC-AUC**: Overall classification performance

### Supporting Metrics
- **Precision**: Minimize false positives (important for fraud)
- **Recall**: Catch all fraudulent transactions
- **Accuracy**: Overall correctness

### Selection Criteria
Best model is selected based on highest F1 score, which is critical for imbalanced fraud detection.

## MLflow Integration

All training runs are logged to MLflow:

**Logged Information:**
- Parameters (hyperparameters)
- Metrics (accuracy, precision, recall, etc.)
- Models (serialized sklearn models)
- Artifacts (feature importance, CV results)

**View Experiments:**
```bash
# Access MLflow UI
open http://localhost:5002

# Compare runs
# Register best models
# View model lineage
```

## Model Deployment Criteria

For a model to be deployed to production:
- Precision ≥ 80%
- Recall ≥ 70%
- F1 Score ≥ 75%

These thresholds are defined in the Airflow DAG (`ml_pipeline_dag.py`).

## Output

### Models Saved
```
./models/
├── logistic_regression.joblib
├── random_forest.joblib
├── gradient_boosting.joblib
├── tuned_random_forest.joblib (if tuning is run)
├── tuned_gradient_boosting.joblib (if tuning is run)
└── scaler.joblib
```

### MLflow Artifacts
- Experiment runs in MLflow UI
- Model registry entries
- Run comparisons and metrics

## Integration

### With Airflow
The `ml_pipeline_dag.py` Airflow DAG orchestrates:
1. Data extraction from Delta Lake
2. Model training (`fraud_detection_trainer.py`)
3. Model evaluation
4. Conditional deployment based on performance

### With FastAPI Serving
Trained models can be loaded by the FastAPI serving application:
```python
import joblib
model = joblib.load('./models/random_forest.joblib')
scaler = joblib.load('./models/scaler.joblib')
```

## Advanced Features

### Cross-Validation
Both training scripts use 5-fold stratified cross-validation to ensure robust model evaluation.

### Imbalanced Data Handling
- Stratified train/test split maintains fraud rate
- F1 score prioritizes both precision and recall
- Can integrate SMOTE or other techniques if needed

### Feature Importance
For tree-based models (Random Forest, Gradient Boosting):
- Feature importance logged to MLflow
- Helps understand which features drive predictions

## Troubleshooting

### Issue: MLflow connection error
```bash
# Check if MLflow server is running
docker ps | grep mlflow

# Restart if needed
docker restart mlflow
```

### Issue: Out of memory during training
```python
# Reduce n_estimators or sample size
# Use n_jobs=1 instead of n_jobs=-1
# Reduce GridSearchCV parameter grid
```

### Issue: Poor model performance
- Check data quality
- Verify feature engineering
- Try different models (XGBoost, LightGBM)
- Adjust class weights for imbalanced data
- Collect more training data

## Future Enhancements

- [ ] Add XGBoost and LightGBM models
- [ ] Implement SMOTE for handling class imbalance
- [ ] Add feature engineering pipeline
- [ ] Implement automated feature selection
- [ ] Add model interpretability (SHAP values)
- [ ] Implement A/B testing framework
- [ ] Add online learning capabilities
- [ ] Create model performance monitoring
- [ ] Add data drift detection

## References

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Fraud Detection Best Practices](https://www.kaggle.com/code/janiobachmann/credit-fraud-dealing-with-imbalanced-datasets)
