"""
Utility functions for Spark Structured Streaming
"""

from config import spark_config
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *


def create_spark_session(app_name: str = None) -> SparkSession:
    """
    Create and configure Spark session with Delta Lake support

    Args:
        app_name: Optional application name override

    Returns:
        Configured SparkSession
    """
    builder = SparkSession.builder

    if app_name:
        builder = builder.appName(app_name)
    else:
        builder = builder.appName(spark_config.app_name)

    # Add Spark configurations
    for key, value in spark_config.configs.items():
        builder = builder.config(key, value)

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel(spark_config.log_level)

    return spark


def get_transaction_schema() -> StructType:
    """
    Get the schema for transaction events

    Returns:
        StructType defining the transaction schema
    """
    return StructType(
        [
            StructField("transaction_id", StringType(), False),
            StructField("user_id", IntegerType(), False),
            StructField("amount", DoubleType(), False),
            StructField("merchant", StringType(), False),
            StructField("timestamp", StringType(), False),
            StructField("is_fraud", BooleanType(), False),
            StructField("payment_method", StringType(), False),
            StructField("location", StringType(), False),
            StructField("device_id", StringType(), False),
        ]
    )


def add_processing_metadata(df: DataFrame) -> DataFrame:
    """
    Add processing metadata columns to a DataFrame

    Args:
        df: Input DataFrame

    Returns:
        DataFrame with additional metadata columns
    """
    return df.withColumn("processing_time", current_timestamp()).withColumn(
        "processing_date", current_date()
    )


def calculate_fraud_score(df: DataFrame) -> DataFrame:
    """
    Calculate a fraud risk score based on transaction patterns

    Args:
        df: DataFrame with transaction data

    Returns:
        DataFrame with fraud_score column added
    """
    return df.withColumn(
        "fraud_score",
        when(col("is_fraud"), 1.0)
        .when(col("amount") > 1000, 0.7)
        .when(col("payment_method") == "crypto", 0.5)
        .otherwise(0.1),
    )


def extract_location_components(df: DataFrame) -> DataFrame:
    """
    Extract city and country from location string

    Args:
        df: DataFrame with location column (format: "City, Country")

    Returns:
        DataFrame with city and country columns
    """
    return df.withColumn("city", split(col("location"), ", ").getItem(0)).withColumn(
        "country", split(col("location"), ", ").getItem(1)
    )


def categorize_amount(df: DataFrame) -> DataFrame:
    """
    Categorize transaction amounts into buckets

    Args:
        df: DataFrame with amount column

    Returns:
        DataFrame with amount_category column
    """
    return df.withColumn(
        "amount_category",
        when(col("amount") < 10, "micro")
        .when(col("amount") < 100, "small")
        .when(col("amount") < 1000, "medium")
        .when(col("amount") < 10000, "large")
        .otherwise("enterprise"),
    )


def write_to_delta(
    df: DataFrame, path: str, mode: str = "append", partition_by: list = None
):
    """
    Write DataFrame to Delta Lake table

    Args:
        df: DataFrame to write
        path: Delta table path
        mode: Write mode (append, overwrite, etc.)
        partition_by: List of columns to partition by
    """
    writer = (
        df.writeStream.format("delta")
        .outputMode(mode)
        .option("checkpointLocation", f"{path}/_checkpoint")
    )

    if partition_by:
        writer = writer.partitionBy(*partition_by)

    return writer.start(path)


def write_to_console(df: DataFrame, mode: str = "append", truncate: bool = False):
    """
    Write DataFrame to console for debugging

    Args:
        df: DataFrame to display
        mode: Output mode
        truncate: Whether to truncate output
    """
    return (
        df.writeStream.format("console")
        .outputMode(mode)
        .option("truncate", truncate)
        .start()
    )
