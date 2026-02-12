#!/usr/bin/env python3
"""Test script for fraud detection API."""

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests")
    exit(1)

import json
import time

def test_prediction_api():
    """Test the fraud detection API with sample data."""
    base_url = "http://localhost:8000"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Starting service...")
        import subprocess
        import os
        # Start the API in background
        subprocess.Popen(['python', 'ml-platform/serving/app.py'])
        time.sleep(3)
        
        # Try again
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Health check passed")
            else:
                print("❌ Health check still failing")
                return
        except:
            print("❌ Still cannot connect to API")
            return
    
    # Test predictions with both model versions
    test_transactions = [
        {
            "user_id": 1234,
            "amount": 50.0,
            "merchant": "Coffee Shop",
            "payment_method": "credit_card",
            "location": "New York"
        },
        {
            "user_id": 5678,
            "amount": 1500.0,
            "merchant": "SUSPICIOUS_STORE",
            "payment_method": "credit_card",
            "location": "Unknown"
        }
    ]
    
    for version in ["v1", "v2"]:
        print(f"\n🧪 Testing model version {version}:")
        
        for i, transaction in enumerate(test_transactions):
            headers = {"X-Model-Version": version, "Content-Type": "application/json"}
            
            try:
                response = requests.post(
                    f"{base_url}/predict",
                    json=transaction,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  Transaction {i+1}: {result['fraud_probability']:.3f} fraud probability "
                          f"({result['response_time_ms']:.1f}ms)")
                else:
                    print(f"  ❌ Prediction failed: {response.text}")
            except Exception as e:
                print(f"  ❌ Request failed: {e}")

if __name__ == "__main__":
    test_prediction_api()
