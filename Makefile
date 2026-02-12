.PHONY: up down logs dbt-run airflow-init seed status demo clean install help

# Main commands
up: 
	cd infra/docker && docker-compose up -d
	@echo "🚀 All services starting... wait 30 seconds then run 'make status'"

down: 
	cd infra/docker && docker-compose down -v
	@echo "🛑 All services stopped and volumes removed"

logs: 
	cd infra/docker && docker-compose logs -f --tail=200

status:
	@echo "=== 🔍 Service Health Check ==="
	@curl -fsS http://localhost:8081/subjects >/dev/null && echo "✅ Schema Registry: OK" || echo "❌ Schema Registry: DOWN"
	@curl -fsS http://localhost:5002/ >/dev/null && echo "✅ MLflow: OK" || echo "❌ MLflow: DOWN"
	@curl -fsS http://localhost:3002/api/health >/dev/null && echo "✅ Grafana: OK" || echo "❌ Grafana: DOWN"
	@curl -fsS http://localhost:8082/health >/dev/null && echo "✅ Airflow: OK" || echo "❌ Airflow: DOWN"
	@curl -fsS http://localhost:9095/-/healthy >/dev/null && echo "✅ Prometheus: OK" || echo "❌ Prometheus: DOWN"

# Rest of Makefile stays the same...
install:
	pip install kafka-python faker requests fastapi uvicorn sentence-transformers faiss-cpu
	pip install dbt-postgres great-expectations
	pre-commit install || echo "⚠️  pre-commit not installed, run: pip install pre-commit"

seed: 
	python data-platform/ingestion/seed_events.py
	@echo "📊 Sample events sent to Kafka"

demo:
	@echo "=== 🎬 Running End-to-End Demo ==="
	@echo "🌐 Check services at:"
	@echo "   - Grafana: http://localhost:3002 (admin/admin)"
	@echo "   - MLflow: http://localhost:5002"
	@echo "   - Airflow: http://localhost:8082 (admin/admin)"
	make seed
	python ml-platform/serving/test_prediction.py
	python ai-platform/rag-service/test_explanation.py

help:
	@echo "🌐 Service URLs:"
	@echo "  - Grafana: http://localhost:3002 (admin/admin)"
	@echo "  - MLflow: http://localhost:5002"
	@echo "  - Airflow: http://localhost:8082 (admin/admin)"
	@echo "  - Prometheus: http://localhost:9095"
	@echo "  - Schema Registry: http://localhost:8081"
	@echo "  - PostgreSQL: localhost:5433"
