#!/usr/bin/env python3
"""Test script for RAG explanation service."""

try:
    import requests
except ImportError:
    print("❌ requests not installed. Run: pip install requests")
    exit(1)

import json
import time

def test_rag_service():
    """Test the RAG explanation service."""
    base_url = "http://localhost:8001"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ RAG service healthy - {health['documents_loaded']} documents loaded")
        else:
            print("❌ RAG service health check failed")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to RAG service. Starting service...")
        import subprocess
        subprocess.Popen(['python', 'ai-platform/rag-service/app.py'])
        time.sleep(5)  # Give more time for model loading
        
        # Try again
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            if response.status_code == 200:
                health = response.json()
                print(f"✅ RAG service healthy - {health['documents_loaded']} documents loaded")
            else:
                print("❌ RAG service still failing")
                return
        except:
            print("❌ Still cannot connect to RAG service")
            return
    
    # Test explanation generation
    test_requests = [
        {
            "transaction_id": "txn_123",
            "fraud_probability": 0.85,
            "amount": 1500.0,
            "merchant": "SUSPICIOUS_STORE",
            "features": {"payment_method": "credit_card", "location": "unknown"}
        },
        {
            "transaction_id": "txn_456",
            "fraud_probability": 0.15,
            "amount": 25.0,
            "merchant": "Coffee Shop",
            "features": {"payment_method": "debit_card", "location": "new_york"}
        }
    ]
    
    print("\n🧠 Testing explanation generation:")
    
    for i, test_request in enumerate(test_requests):
        try:
            response = requests.post(
                f"{base_url}/explain",
                json=test_request,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n  Test {i+1}:")
                print(f"    Explanation: {result['explanation']}")
                print(f"    Confidence: {result['confidence']:.3f}")
                print(f"    Sources: {len(result['sources'])} documents")
            else:
                print(f"  ❌ Explanation failed: {response.text}")
        except Exception as e:
            print(f"  ❌ Request failed: {e}")

if __name__ == "__main__":
    test_rag_service()
