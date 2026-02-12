"""
Configuration for Spark Streaming Jobs
"""

import os
from dataclasses import dataclass


@dataclass
class KafkaConfig:
    """Kafka connection configuration"""

    bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    schema_registry_url: str = os.getenv("SCHEMA_REGISTRY_URL", "http://localhost:8081")
    topic: str = "ecommerce.transactions"
    consumer_group: str = "spark-streaming-consumer"


@dataclass
class DeltaConfig:
    """Delta Lake storage configuration"""

    base_path: str = os.getenv("DELTA_BASE_PATH", "/tmp/delta-lake")
    bronze_path: str = f"{base_path}/bronze/transactions"
    silver_path: str = f"{base_path}/silver/transactions"
    gold_path: str = f"{base_path}/gold/transactions"
    checkpoint_path: str = f"{base_path}/checkpoints"


@dataclass
class SparkConfig:
    """Spark session configuration"""

    app_name: str = "data-platform-streaming"
    master: str = os.getenv("SPARK_MASTER", "local[*]")
    log_level: str = "WARN"

    # Spark configurations
    configs = {
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        "spark.sql.streaming.checkpointLocation": DeltaConfig().checkpoint_path,
        "spark.streaming.stopGracefullyOnShutdown": "true",
        "spark.sql.shuffle.partitions": "4",
    }


# Initialize configurations
kafka_config = KafkaConfig()
delta_config = DeltaConfig()
spark_config = SparkConfig()
