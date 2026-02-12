"""
Real-time Fraud Detection using Spark Structured Streaming
Detects fraudulent transactions based on patterns and rules
"""

from config import delta_config
from pyspark.sql.functions import *
from pyspark.sql.types import *
from pyspark.sql.window import Window
from utils import add_processing_metadata, create_spark_session


def calculate_fraud_score(df):
    """
    Calculate fraud risk score based on multiple factors

    Scoring criteria:
    - Known fraud flag: +50 points
    - High transaction amount (>$5000): +30 points
    - Unusual payment method (crypto): +20 points
    - High-risk country: +15 points
    - Late night transaction (11 PM - 5 AM): +10 points
    - Weekend transaction: +5 points
    """
    df = df.withColumn("fraud_score", lit(0))

    # Known fraud
    df = df.withColumn(
        "fraud_score",
        when(col("is_fraud"), col("fraud_score") + 50).otherwise(col("fraud_score")),
    )

    # High amount
    df = df.withColumn(
        "fraud_score",
        when(col("amount") > 5000, col("fraud_score") + 30).otherwise(
            col("fraud_score")
        ),
    )

    # Crypto payments
    df = df.withColumn(
        "fraud_score",
        when(col("payment_method") == "crypto", col("fraud_score") + 20).otherwise(
            col("fraud_score")
        ),
    )

    # High-risk countries (example list)
    high_risk_countries = ["Nigeria", "Russia", "China"]
    df = df.withColumn(
        "fraud_score",
        when(
            col("country").isin(high_risk_countries), col("fraud_score") + 15
        ).otherwise(col("fraud_score")),
    )

    # Late night transactions (23:00 - 05:00)
    df = df.withColumn(
        "fraud_score",
        when(
            (col("transaction_hour") >= 23) | (col("transaction_hour") <= 5),
            col("fraud_score") + 10,
        ).otherwise(col("fraud_score")),
    )

    # Weekend transactions
    df = df.withColumn(
        "fraud_score",
        when(col("is_weekend"), col("fraud_score") + 5).otherwise(col("fraud_score")),
    )

    return df


def detect_velocity_fraud(df):
    """
    Detect fraud based on transaction velocity
    - Multiple transactions in short time window
    - Multiple devices for same user
    """
    # Define time window for velocity check (30 minutes)
    window_spec = (
        Window.partitionBy("user_id")
        .orderBy(col("timestamp_parsed").cast("long"))
        .rangeBetween(-1800, 0)
    )  # 30 minutes in seconds

    # Count transactions in window
    df = df.withColumn("tx_count_30min", count("*").over(window_spec))

    # Flag high velocity (>5 transactions in 30 minutes)
    df = df.withColumn(
        "is_high_velocity", when(col("tx_count_30min") > 5, True).otherwise(False)
    )

    # Increase fraud score for high velocity
    df = df.withColumn(
        "fraud_score",
        when(col("is_high_velocity"), col("fraud_score") + 25).otherwise(
            col("fraud_score")
        ),
    )

    return df


def classify_fraud_risk(df):
    """
    Classify transactions into risk categories based on fraud score
    """
    df = df.withColumn(
        "risk_level",
        when(col("fraud_score") >= 75, "CRITICAL")
        .when(col("fraud_score") >= 50, "HIGH")
        .when(col("fraud_score") >= 25, "MEDIUM")
        .when(col("fraud_score") >= 10, "LOW")
        .otherwise("MINIMAL"),
    )

    df = df.withColumn(
        "requires_review", when(col("fraud_score") >= 50, True).otherwise(False)
    )

    return df


def main():
    """
    Main fraud detection streaming pipeline
    """
    print("=" * 80)
    print("Starting Real-Time Fraud Detection Pipeline")
    print("=" * 80)

    spark = create_spark_session("fraud-detection-stream")

    try:
        # Read from Silver layer
        print(f"Reading from Silver layer: {delta_config.silver_path}")

        silver_stream = spark.readStream.format("delta").load(delta_config.silver_path)

        # Apply fraud detection logic
        fraud_df = calculate_fraud_score(silver_stream)
        fraud_df = detect_velocity_fraud(fraud_df)
        fraud_df = classify_fraud_risk(fraud_df)

        # Add metadata
        fraud_df = add_processing_metadata(fraud_df)

        # Select final columns
        fraud_df = fraud_df.select(
            "transaction_id",
            "user_id",
            "amount",
            "merchant",
            "payment_method",
            "location",
            "country",
            "device_id",
            "timestamp_parsed",
            "transaction_hour",
            "is_weekend",
            "is_fraud",
            "fraud_score",
            "risk_level",
            "requires_review",
            "is_high_velocity",
            "tx_count_30min",
            "processing_time",
        )

        # Write to fraud detection Delta table
        fraud_output_path = f"{delta_config.base_path}/fraud_detection"

        print(f"Writing fraud detection results to: {fraud_output_path}")

        query = (
            fraud_df.writeStream.format("delta")
            .outputMode("append")
            .option("checkpointLocation", f"{fraud_output_path}/_checkpoint")
            .partitionBy("risk_level")
            .start(fraud_output_path)
        )

        # Also write high-risk transactions to console for immediate alerting
        high_risk_df = fraud_df.filter(col("risk_level").isin(["CRITICAL", "HIGH"]))

        console_query = (
            high_risk_df.writeStream.format("console")
            .outputMode("append")
            .option("truncate", False)
            .start()
        )

        print("\n" + "=" * 80)
        print("Fraud Detection Pipeline Started Successfully!")
        print(f"Output: {fraud_output_path}")
        print("High-risk transactions will be printed to console")
        print("=" * 80)

        query.awaitTermination()
        console_query.awaitTermination()

    except Exception as e:
        print(f"Error in fraud detection pipeline: {str(e)}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
