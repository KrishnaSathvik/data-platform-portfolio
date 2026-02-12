#!/usr/bin/env python3
"""
Sample Kafka producer for e-commerce transaction events.
Generates realistic transaction data for testing the platform.
"""

import json
import random
import time
from datetime import datetime, timedelta

try:
    from kafka import KafkaProducer
except ImportError:
    print("❌ kafka-python not installed. Run: pip install kafka-python")
    exit(1)

try:
    from faker import Faker
except ImportError:
    print("❌ faker not installed. Run: pip install faker")
    exit(1)

fake = Faker()

def create_producer():
    """Create Kafka producer with JSON serialization."""
    return KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: str(k).encode('utf-8')
    )

def generate_transaction():
    """Generate a realistic e-commerce transaction."""
    transaction_id = fake.uuid4()
    user_id = random.randint(1000, 9999)
    
    # Create realistic fraud patterns
    is_fraud = random.random() < 0.05  # 5% fraud rate
    
    if is_fraud:
        amount = random.uniform(500, 5000)  # High amounts more likely fraud
        merchant = random.choice(['SUSPICIOUS_STORE', 'FAKE_MERCHANT', 'SCAM_SHOP'])
    else:
        amount = random.uniform(5, 500)
        merchant = fake.company()
    
    return {
        'transaction_id': transaction_id,
        'user_id': user_id,
        'amount': round(amount, 2),
        'merchant': merchant,
        'timestamp': datetime.now().isoformat(),
        'is_fraud': is_fraud,
        'payment_method': random.choice(['credit_card', 'debit_card', 'paypal']),
        'location': fake.city(),
        'device_id': fake.uuid4()
    }

def main():
    """Send sample transactions to Kafka."""
    try:
        producer = create_producer()
        topic = 'transactions'
        
        print(f"🚀 Starting to send events to topic '{topic}'...")
        
        for i in range(100):  # Send 100 sample transactions
            transaction = generate_transaction()
            
            # Use user_id as partition key for consistent routing
            producer.send(
                topic=topic,
                key=transaction['user_id'],
                value=transaction
            )
            
            if (i + 1) % 10 == 0:
                print(f"📊 Sent {i + 1} transactions...")
            
            time.sleep(0.1)  # Small delay to simulate real traffic
            
        producer.flush()
        print("✅ All events sent successfully!")
        
    except Exception as e:
        print(f"❌ Error sending events: {e}")
        print("💡 Make sure Kafka is running: make up")
    finally:
        if 'producer' in locals():
            producer.close()

if __name__ == '__main__':
    main()
