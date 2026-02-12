# Spark Structured Streaming Processing

This directory contains Spark Structured Streaming jobs for real-time data processing.

## Architecture

```
Kafka → Spark Structured Streaming → Delta Lake (Medallion Architecture)
                                    ↓
                            Bronze → Silver → Gold
```

## Components

### 1. `kafka_to_delta.py` - Main Streaming Pipeline
Implements the medallion architecture with three layers:

- **Bronze Layer**: Raw data ingestion from Kafka
  - Minimal transformation
  - Preserves all original data
  - Adds ingestion metadata

- **Silver Layer**: Cleaned and enriched data
  - Data quality checks
  - Type conversions
  - Business logic enrichment
  - Deduplication
  - Location parsing (city, country)
  - Amount categorization

- **Gold Layer**: Business-level aggregations
  - 10-minute windowed aggregations
  - Metrics by merchant, payment method, country
  - Fraud rate calculations
  - Ready for analytics/BI

### 2. `fraud_detection_stream.py` - Real-time Fraud Detection
Detects fraudulent transactions using multiple signals:

**Fraud Scoring Criteria:**
- Known fraud flag: +50 points
- High amount (>$5000): +30 points
- Crypto payments: +20 points
- High-risk countries: +15 points
- Late night (11 PM - 5 AM): +10 points
- Weekend: +5 points

**Velocity Fraud Detection:**
- Tracks transaction count in 30-minute windows
- Flags >5 transactions in 30 minutes as high velocity
- Adds +25 to fraud score

**Risk Classification:**
- CRITICAL: Score ≥ 75
- HIGH: Score ≥ 50
- MEDIUM: Score ≥ 25
- LOW: Score ≥ 10
- MINIMAL: Score < 10

### 3. `aggregations_stream.py` - Business Metrics
Calculates real-time business KPIs:

**Merchant Aggregations** (15-min sliding, 5-min updates):
- Transaction counts and revenue
- Average transaction value
- Fraud rate by merchant
- Customer and device counts

**User Aggregations** (1-hour tumbling):
- User spending patterns
- Merchant diversity
- Payment method usage
- Suspicious behavior detection

**Country Aggregations** (30-min tumbling):
- Geographic transaction volume
- Regional fraud rates
- Active users and merchants by location

**Hourly Platform Summary**:
- Overall platform statistics
- Payment method distribution
- Fraud rates
- High-value transaction rates

### 4. `config.py` - Configuration Management
Centralized configuration for:
- Kafka connection settings
- Delta Lake paths
- Spark session configuration

### 5. `utils.py` - Utility Functions
Reusable functions for:
- Spark session creation
- Schema definitions
- Metadata addition
- Delta Lake writes

## Usage

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Streaming Jobs

**Main Pipeline (Bronze → Silver → Gold):**
```bash
python kafka_to_delta.py
```

**Fraud Detection:**
```bash
python fraud_detection_stream.py
```

**Real-time Aggregations:**
```bash
python aggregations_stream.py
```

### Environment Variables

Configure in `.env` file:
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SCHEMA_REGISTRY_URL=http://localhost:8081
DELTA_BASE_PATH=/tmp/delta-lake
SPARK_MASTER=local[*]
```

## Delta Lake Output Structure

```
/tmp/delta-lake/
├── bronze/
│   └── transactions/           # Raw Kafka data
├── silver/
│   └── transactions/           # Cleaned & enriched
├── gold/
│   └── transactions/           # Business aggregations
├── fraud_detection/            # Fraud scores & classifications
└── aggregations/
    ├── merchant/               # Merchant metrics
    ├── user/                   # User behavior
    ├── country/                # Geographic metrics
    └── hourly_summary/         # Platform-wide KPIs
```

## Monitoring

All streams expose Spark metrics that can be scraped by Prometheus:
- Processing rates
- Batch durations
- Watermark delays
- Record counts

## Watermarking & Late Data

- Bronze: No watermark (accepts all data)
- Silver: 10-minute watermark
- Gold: 10-minute watermark
- Aggregations: Varies by stream (15min - 1hour)

## Checkpointing

Each stream maintains checkpoints for fault tolerance:
- Enables exactly-once processing
- Allows recovery from failures
- Stored alongside Delta tables

## Integration with dbt

The Silver and Gold Delta tables feed into dbt models:
```
Delta Silver → dbt staging → dbt marts → Analytics
```

## Performance Tuning

- Adjust `spark.sql.shuffle.partitions` for your cluster size
- Configure memory settings based on data volume
- Use `maxFilesPerTrigger` to control micro-batch size
- Monitor watermark delays and adjust if needed

## Troubleshooting

**Issue:** Stream not starting
- Check Kafka connectivity
- Verify topic exists
- Check Schema Registry

**Issue:** High latency
- Increase parallelism
- Adjust trigger intervals
- Check for data skew

**Issue:** Checkpoint errors
- Delete checkpoint directory and restart
- Verify Delta Lake permissions

## Future Enhancements

- [ ] Add machine learning fraud model
- [ ] Implement session windowing for user journeys
- [ ] Add data quality metrics
- [ ] Integrate with alerting system (PagerDuty, Slack)
- [ ] Add A/B testing framework
