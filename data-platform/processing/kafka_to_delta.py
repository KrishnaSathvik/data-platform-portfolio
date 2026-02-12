"""
Spark Structured Streaming: Kafka to Delta Lake
Implements medallion architecture (Bronze -> Silver -> Gold layers)
"""

from config import delta_config, kafka_config
from pyspark.sql.functions import *
from pyspark.sql.types import *
from utils import (
    add_processing_metadata,
    create_spark_session,
    get_transaction_schema,
    write_to_delta,
)


def create_bronze_layer(spark):
    """
    Bronze Layer: Raw data ingestion from Kafka
    - Minimal transformation
    - Preserve all original data
    - Add ingestion metadata
    """
    print("Starting Bronze Layer: Reading from Kafka...")

    # Read from Kafka
    raw_stream = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_config.bootstrap_servers)
        .option("subscribe", kafka_config.topic)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
    )

    # Parse JSON from Kafka value
    transaction_schema = get_transaction_schema()

    bronze_df = raw_stream.select(
        col("key").cast("string").alias("kafka_key"),
        from_json(col("value").cast("string"), transaction_schema).alias("data"),
        col("topic"),
        col("partition"),
        col("offset"),
        col("timestamp").alias("kafka_timestamp"),
    ).select("kafka_key", "data.*", "topic", "partition", "offset", "kafka_timestamp")

    # Add ingestion metadata
    bronze_df = add_processing_metadata(bronze_df)

    print(f"Writing Bronze Layer to: {delta_config.bronze_path}")

    # Write to Bronze Delta table
    query = write_to_delta(
        bronze_df, delta_config.bronze_path, partition_by=["processing_date"]
    )

    return query


def create_silver_layer(spark):
    """
    Silver Layer: Cleaned and enriched data
    - Data quality checks
    - Type conversions
    - Business logic enrichment
    - Deduplication
    """
    print("Starting Silver Layer: Reading from Bronze Delta...")

    # Read from Bronze layer
    bronze_df = spark.readStream.format("delta").load(delta_config.bronze_path)

    # Clean and enrich data
    silver_df = (
        bronze_df.filter(col("transaction_id").isNotNull())
        .filter(col("amount") > 0)
        .withColumn("timestamp_parsed", to_timestamp(col("timestamp")))
        .withColumn("transaction_date", to_date(col("timestamp_parsed")))
        .withColumn("transaction_hour", hour(col("timestamp_parsed")))
        .withColumn("transaction_day_of_week", dayofweek(col("timestamp_parsed")))
        .withColumn("is_high_value", when(col("amount") > 1000, True).otherwise(False))
        .withColumn(
            "is_weekend",
            when(col("transaction_day_of_week").isin([1, 7]), True).otherwise(False),
        )
    )

    # Extract location components
    silver_df = silver_df.withColumn(
        "city", split(col("location"), ", ").getItem(0)
    ).withColumn("country", split(col("location"), ", ").getItem(1))

    # Categorize amounts
    silver_df = silver_df.withColumn(
        "amount_category",
        when(col("amount") < 10, "micro")
        .when(col("amount") < 100, "small")
        .when(col("amount") < 1000, "medium")
        .when(col("amount") < 10000, "large")
        .otherwise("enterprise"),
    )

    # Add processing metadata
    silver_df = add_processing_metadata(silver_df)

    # Select final columns for Silver layer
    silver_df = silver_df.select(
        "transaction_id",
        "user_id",
        "amount",
        "amount_category",
        "is_high_value",
        "merchant",
        "payment_method",
        "location",
        "city",
        "country",
        "device_id",
        "is_fraud",
        "timestamp_parsed",
        "transaction_date",
        "transaction_hour",
        "transaction_day_of_week",
        "is_weekend",
        "processing_time",
        "processing_date",
    )

    print(f"Writing Silver Layer to: {delta_config.silver_path}")

    # Write to Silver Delta table (deduplicated)
    query = (
        silver_df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{delta_config.silver_path}/_checkpoint")
        .option("mergeSchema", "true")
        .partitionBy("transaction_date")
        .start(delta_config.silver_path)
    )

    return query


def create_gold_layer(spark):
    """
    Gold Layer: Business-level aggregations
    - Aggregated metrics
    - Business KPIs
    - Ready for analytics/BI tools
    """
    print("Starting Gold Layer: Reading from Silver Delta...")

    # Read from Silver layer
    silver_df = spark.readStream.format("delta").load(delta_config.silver_path)

    # Create windowed aggregations (10-minute windows)
    gold_df = (
        silver_df.withWatermark("timestamp_parsed", "10 minutes")
        .groupBy(
            window(col("timestamp_parsed"), "10 minutes"),
            col("merchant"),
            col("payment_method"),
            col("country"),
        )
        .agg(
            count("*").alias("transaction_count"),
            sum("amount").alias("total_amount"),
            avg("amount").alias("avg_amount"),
            max("amount").alias("max_amount"),
            min("amount").alias("min_amount"),
            sum(when(col("is_fraud"), 1).otherwise(0)).alias("fraud_count"),
            sum(when(col("is_high_value"), 1).otherwise(0)).alias("high_value_count"),
            countDistinct("user_id").alias("unique_users"),
            countDistinct("device_id").alias("unique_devices"),
        )
    )

    # Calculate fraud rate
    gold_df = gold_df.withColumn(
        "fraud_rate", (col("fraud_count") / col("transaction_count")) * 100
    )

    # Add metadata
    gold_df = gold_df.withColumn("aggregation_time", current_timestamp())

    print(f"Writing Gold Layer to: {delta_config.gold_path}")

    # Write to Gold Delta table
    query = (
        gold_df.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{delta_config.gold_path}/_checkpoint")
        .option("mergeSchema", "true")
        .start(delta_config.gold_path)
    )

    return query


def main():
    """
    Main entry point for Kafka to Delta streaming pipeline
    Implements full medallion architecture
    """
    print("=" * 80)
    print("Starting Kafka to Delta Lake Streaming Pipeline")
    print("Medallion Architecture: Bronze -> Silver -> Gold")
    print("=" * 80)

    # Create Spark session
    spark = create_spark_session("kafka-to-delta-pipeline")

    try:
        # Start all three layers
        bronze_query = create_bronze_layer(spark)
        silver_query = create_silver_layer(spark)
        gold_query = create_gold_layer(spark)

        print("\n" + "=" * 80)
        print("All streaming queries started successfully!")
        print("=" * 80)
        print(f"Bronze Layer: {delta_config.bronze_path}")
        print(f"Silver Layer: {delta_config.silver_path}")
        print(f"Gold Layer: {delta_config.gold_path}")
        print("=" * 80)

        # Wait for termination
        bronze_query.awaitTermination()
        silver_query.awaitTermination()
        gold_query.awaitTermination()

    except Exception as e:
        print(f"Error in streaming pipeline: {str(e)}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
