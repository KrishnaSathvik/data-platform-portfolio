# Platform Architecture

```mermaid
flowchart LR
    subgraph "Data Ingestion"
        P[Event Producer] --> K((Kafka))
        K --> SR[Schema Registry]
    end
    
    subgraph "Stream Processing"
        K --> SP[Spark Streaming]
        SP --> B[(Bronze Layer)]
        B --> S[(Silver Layer)]
        S --> G[(Gold Layer)]
    end
    
    subgraph "Analytics Warehouse"
        G --> DBT[dbt Transforms]
        DBT --> WH[(Data Warehouse)]
        AF[Airflow] --> DBT
    end
    
    subgraph "ML Platform"
        WH --> FS[(Feature Store)]
        FS --> ML[MLflow Training]
        ML --> API[Model API]
    end
    
    subgraph "AI Platform"
        API --> RAG[RAG Service]
        RAG --> VDB[(Vector DB)]
        RAG --> LLM[LLM]
    end
    
    subgraph "Observability"
        PROM[Prometheus] --> GRAF[Grafana]
        K --> KE[Kafka Exporter]
        KE --> PROM
        API --> PROM
        RAG --> PROM
    end
    
    RAG --> USERS[Business Users]
    GRAF --> USERS
```

## Data Flow

1. **Events** are produced to Kafka with schema validation
2. **Spark Streaming** processes events into Bronze/Silver/Gold layers
3. **dbt** transforms data for analytics in the warehouse
4. **MLflow** trains models on feature data
5. **FastAPI** serves models with A/B testing
6. **RAG service** explains predictions using vector search
7. **Prometheus + Grafana** monitor the entire platform
