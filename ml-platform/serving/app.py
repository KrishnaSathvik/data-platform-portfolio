#!/usr/bin/env python3
"""
FastAPI service for serving fraud detection models.
Includes A/B testing via header routing.
"""

try:
    from fastapi import FastAPI, HTTPException, Header
    from pydantic import BaseModel
except ImportError:
    print("❌ FastAPI not installed. Run: pip install fastapi uvicorn")
    exit(1)

from typing import Optional
import time

app = FastAPI(title="Fraud Detection API", version="1.0.0")

# Mock models for A/B testing
models = {
    "v1": {"accuracy": 0.85, "name": "Logistic Regression"},
    "v2": {"accuracy": 0.88, "name": "Random Forest"}
}

class TransactionRequest(BaseModel):
    user_id: int
    amount: float
    merchant: str
    payment_method: str
    location: str

class PredictionResponse(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_fraud: bool
    model_version: str
    response_time_ms: float

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "models": list(models.keys())}

@app.post("/predict", response_model=PredictionResponse)
async def predict_fraud(
    transaction: TransactionRequest,
    x_model_version: Optional[str] = Header(default="v1")
):
    """Predict fraud probability for a transaction."""
    start_time = time.time()
    
    # Validate model version
    if x_model_version not in models:
        x_model_version = "v1"
    
    # Mock prediction logic (replace with actual model)
    # Higher amounts and suspicious merchants = higher fraud probability
    base_probability = min(transaction.amount / 1000, 0.8)
    
    if "SUSPICIOUS" in transaction.merchant.upper():
        base_probability += 0.3
    
    # Add model version bias for A/B testing
    if x_model_version == "v2":
        base_probability *= 0.95  # Slightly more conservative
    
    fraud_probability = min(max(base_probability, 0.0), 1.0)
    is_fraud = fraud_probability > 0.5
    
    response_time_ms = (time.time() - start_time) * 1000
    
    return PredictionResponse(
        transaction_id=f"txn_{int(time.time())}",
        fraud_probability=round(fraud_probability, 3),
        is_fraud=is_fraud,
        model_version=x_model_version,
        response_time_ms=round(response_time_ms, 2)
    )

@app.get("/metrics")
async def get_metrics():
    """Expose metrics for monitoring."""
    return {
        "model_versions": models,
        "endpoint_count": 2,
        "status": "operational"
    }

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("❌ uvicorn not installed. Run: pip install uvicorn")
