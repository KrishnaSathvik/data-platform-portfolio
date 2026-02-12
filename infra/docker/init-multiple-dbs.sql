-- Create databases for warehouse, mlflow, and airflow
CREATE DATABASE warehouse;
CREATE USER dbt WITH PASSWORD 'dbt_password';
GRANT ALL PRIVILEGES ON DATABASE warehouse TO dbt;

CREATE DATABASE mlflow;
CREATE USER mlflow WITH PASSWORD 'mlflow_pwd';
GRANT ALL PRIVILEGES ON DATABASE mlflow TO mlflow;

CREATE DATABASE airflow;
CREATE USER airflow WITH PASSWORD 'airflow_pwd';
GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
