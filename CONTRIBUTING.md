# Contributing to Data Platform Portfolio

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <repo> data-platform-portfolio
   cd data-platform-portfolio
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Start services:**
   ```bash
   make up
   ```

3. **Verify everything works:**
   ```bash
   make status
   make demo
   ```

## Development Workflow

1. **Install development dependencies:**
   ```bash
   make install
   ```

2. **Make changes to code**

3. **Test your changes:**
   ```bash
   make demo
   ```

4. **Commit with pre-commit hooks:**
   ```bash
   git add .
   git commit -m "Your change description"
   ```

## Service URLs

- **Kafka:** localhost:9092
- **Schema Registry:** http://localhost:8081
- **MLflow:** http://localhost:5002
- **Airflow:** http://localhost:8082 (admin/admin)
- **Grafana:** http://localhost:3002 (admin/admin)
- **Prometheus:** http://localhost:9095

## Troubleshooting

### Services won't start
```bash
make down
make clean
make up
```

### Out of disk space
```bash
docker system prune -f
```

### Kafka connection issues
- Check if all services are running: `make status`
- View logs: `make logs`
- Restart services: `make down && make up`
