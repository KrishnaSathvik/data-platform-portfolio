"""
Real-time Aggregations using Spark Structured Streaming
Calculates business metrics and KPIs in real-time
"""

from config import delta_config
from pyspark.sql.functions import *
from pyspark.sql.types import *
from utils import create_spark_session


def create_merchant_aggregations(spark):
    """
    Aggregate transactions by merchant with sliding windows
    """
    print("Creating merchant aggregations...")

    # Read from Silver layer
    silver_stream = spark.readStream.format("delta").load(delta_config.silver_path)

    # 15-minute sliding window, updating every 5 minutes
    merchant_agg = (
        silver_stream.withWatermark("timestamp_parsed", "15 minutes")
        .groupBy(
            window(col("timestamp_parsed"), "15 minutes", "5 minutes"),
            col("merchant"),
            col("payment_method"),
        )
        .agg(
            count("*").alias("total_transactions"),
            sum("amount").alias("total_revenue"),
            avg("amount").alias("avg_transaction_value"),
            max("amount").alias("max_transaction"),
            min("amount").alias("min_transaction"),
            stddev("amount").alias("amount_stddev"),
            sum(when(col("is_fraud"), 1).otherwise(0)).alias("fraud_count"),
            countDistinct("user_id").alias("unique_customers"),
            countDistinct("device_id").alias("unique_devices"),
            sum(when(col("is_high_value"), 1).otherwise(0)).alias("high_value_count"),
        )
    )

    # Calculate derived metrics
    merchant_agg = (
        merchant_agg.withColumn(
            "fraud_rate", (col("fraud_count") / col("total_transactions")) * 100
        )
        .withColumn(
            "high_value_rate",
            (col("high_value_count") / col("total_transactions")) * 100,
        )
        .withColumn(
            "avg_devices_per_user", col("unique_devices") / col("unique_customers")
        )
        .withColumn("aggregation_timestamp", current_timestamp())
    )

    # Write to Delta
    output_path = f"{delta_config.base_path}/aggregations/merchant"

    query = (
        merchant_agg.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{output_path}/_checkpoint")
        .start(output_path)
    )

    return query


def create_user_aggregations(spark):
    """
    Aggregate transactions by user for behavior analysis
    """
    print("Creating user aggregations...")

    silver_stream = spark.readStream.format("delta").load(delta_config.silver_path)

    # 1-hour tumbling window
    user_agg = (
        silver_stream.withWatermark("timestamp_parsed", "1 hour")
        .groupBy(
            window(col("timestamp_parsed"), "1 hour"), col("user_id"), col("country")
        )
        .agg(
            count("*").alias("transaction_count"),
            sum("amount").alias("total_spent"),
            avg("amount").alias("avg_amount_per_transaction"),
            countDistinct("merchant").alias("unique_merchants"),
            countDistinct("payment_method").alias("unique_payment_methods"),
            countDistinct("device_id").alias("unique_devices_used"),
            max("amount").alias("largest_transaction"),
            sum(when(col("is_fraud"), 1).otherwise(0)).alias("fraud_transactions"),
            sum(when(col("is_weekend"), 1).otherwise(0)).alias("weekend_transactions"),
        )
    )

    # Calculate user behavior metrics
    user_agg = (
        user_agg.withColumn(
            "is_suspicious",
            when(
                (col("unique_devices_used") > 3)
                | (col("fraud_transactions") > 0)
                | (col("transaction_count") > 20),
                True,
            ).otherwise(False),
        )
        .withColumn(
            "weekend_ratio", col("weekend_transactions") / col("transaction_count")
        )
        .withColumn("aggregation_timestamp", current_timestamp())
    )

    # Write to Delta
    output_path = f"{delta_config.base_path}/aggregations/user"

    query = (
        user_agg.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{output_path}/_checkpoint")
        .start(output_path)
    )

    return query


def create_country_aggregations(spark):
    """
    Aggregate transactions by country/region for geographic analysis
    """
    print("Creating country aggregations...")

    silver_stream = spark.readStream.format("delta").load(delta_config.silver_path)

    # 30-minute tumbling window
    country_agg = (
        silver_stream.withWatermark("timestamp_parsed", "30 minutes")
        .groupBy(
            window(col("timestamp_parsed"), "30 minutes"), col("country"), col("city")
        )
        .agg(
            count("*").alias("transaction_volume"),
            sum("amount").alias("total_value"),
            avg("amount").alias("avg_transaction_size"),
            countDistinct("user_id").alias("active_users"),
            countDistinct("merchant").alias("active_merchants"),
            sum(when(col("is_fraud"), 1).otherwise(0)).alias("fraud_count"),
            sum(when(col("amount_category") == "enterprise", 1).otherwise(0)).alias(
                "enterprise_transactions"
            ),
        )
    )

    # Calculate regional metrics
    country_agg = (
        country_agg.withColumn(
            "fraud_percentage", (col("fraud_count") / col("transaction_volume")) * 100
        )
        .withColumn(
            "enterprise_percentage",
            (col("enterprise_transactions") / col("transaction_volume")) * 100,
        )
        .withColumn("avg_value_per_user", col("total_value") / col("active_users"))
        .withColumn("aggregation_timestamp", current_timestamp())
    )

    # Write to Delta
    output_path = f"{delta_config.base_path}/aggregations/country"

    query = (
        country_agg.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{output_path}/_checkpoint")
        .start(output_path)
    )

    return query


def create_hourly_summary(spark):
    """
    Create overall platform hourly summary statistics
    """
    print("Creating hourly summary aggregations...")

    silver_stream = spark.readStream.format("delta").load(delta_config.silver_path)

    # 1-hour tumbling window with global aggregations
    hourly_summary = (
        silver_stream.withWatermark("timestamp_parsed", "1 hour")
        .groupBy(window(col("timestamp_parsed"), "1 hour"))
        .agg(
            count("*").alias("total_transactions"),
            sum("amount").alias("total_volume"),
            avg("amount").alias("avg_transaction_value"),
            countDistinct("user_id").alias("total_users"),
            countDistinct("merchant").alias("total_merchants"),
            countDistinct("device_id").alias("total_devices"),
            countDistinct("country").alias("countries_active"),
            sum(when(col("is_fraud"), 1).otherwise(0)).alias("fraud_transactions"),
            sum(when(col("is_high_value"), 1).otherwise(0)).alias(
                "high_value_transactions"
            ),
            sum(when(col("payment_method") == "credit_card", 1).otherwise(0)).alias(
                "credit_card_tx"
            ),
            sum(when(col("payment_method") == "debit_card", 1).otherwise(0)).alias(
                "debit_card_tx"
            ),
            sum(when(col("payment_method") == "crypto", 1).otherwise(0)).alias(
                "crypto_tx"
            ),
            sum(when(col("payment_method") == "bank_transfer", 1).otherwise(0)).alias(
                "bank_transfer_tx"
            ),
        )
    )

    # Calculate platform KPIs
    hourly_summary = (
        hourly_summary.withColumn(
            "platform_fraud_rate",
            (col("fraud_transactions") / col("total_transactions")) * 100,
        )
        .withColumn(
            "high_value_rate",
            (col("high_value_transactions") / col("total_transactions")) * 100,
        )
        .withColumn(
            "avg_transactions_per_user", col("total_transactions") / col("total_users")
        )
        .withColumn(
            "credit_card_percentage",
            (col("credit_card_tx") / col("total_transactions")) * 100,
        )
        .withColumn("aggregation_timestamp", current_timestamp())
    )

    # Write to Delta
    output_path = f"{delta_config.base_path}/aggregations/hourly_summary"

    query = (
        hourly_summary.writeStream.format("delta")
        .outputMode("append")
        .option("checkpointLocation", f"{output_path}/_checkpoint")
        .start(output_path)
    )

    return query


def main():
    """
    Main aggregations streaming pipeline
    Runs multiple aggregation streams in parallel
    """
    print("=" * 80)
    print("Starting Real-Time Aggregations Pipeline")
    print("Running Multiple Aggregation Streams:")
    print("  1. Merchant Aggregations (15-min sliding window)")
    print("  2. User Aggregations (1-hour tumbling window)")
    print("  3. Country Aggregations (30-min tumbling window)")
    print("  4. Hourly Platform Summary")
    print("=" * 80)

    spark = create_spark_session("aggregations-stream")

    try:
        # Start all aggregation streams
        merchant_query = create_merchant_aggregations(spark)
        user_query = create_user_aggregations(spark)
        country_query = create_country_aggregations(spark)
        hourly_query = create_hourly_summary(spark)

        print("\n" + "=" * 80)
        print("All Aggregation Streams Started Successfully!")
        print(f"Base path: {delta_config.base_path}/aggregations/")
        print("=" * 80)

        # Wait for termination
        merchant_query.awaitTermination()
        user_query.awaitTermination()
        country_query.awaitTermination()
        hourly_query.awaitTermination()

    except Exception as e:
        print(f"Error in aggregations pipeline: {str(e)}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
