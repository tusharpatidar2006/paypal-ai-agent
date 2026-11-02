.PHONY: help setup fetch-models fetch-datasets corpora calibrate test test-fast verify-invariants lint dev web eval redteam demo smoke-paypal smoke-mcp report docker clean

help:
	@echo "Clean Room - Make targets"
	@echo ""
	@echo "  setup            Install Python dependencies"
	@echo "  fetch-models     Download ML models (DeBERTa, fastembed)"
	@echo "  fetch-datasets   Download adversarial-test-data datasets"
	@echo "  corpora          Build attack corpora"
	@echo "  calibrate        Calibrate detection thresholds"
	@echo "  test             Run all tests"
	@echo "  test-fast        Run fast tests only (no e2e)"
	@echo "  verify-invariants Run security invariant tests"
	@echo "  lint             Run ruff and mypy"
	@echo "  dev              Run backend dev server"
	@echo "  web              Build web UI"
	@echo "  eval             Run full evaluation harness"
	@echo "  redteam          Run red team generation"
	@echo "  demo             Run demo scenario"
	@echo "  smoke-paypal     Test PayPal sandbox connection"
	@echo "  smoke-mcp        Test PayPal MCP adapter"
	@echo "  report           Generate reports/"
	@echo "  docker           Build Docker image"
	@echo "  clean            Remove build artifacts"

setup:
	python -m pip install --upgrade pip
	pip install -e ".[dev]"
	@echo "✓ Base dependencies installed"
	@echo "Optional: pip install -e '.[full]' for full detector profile"

fetch-models:
	python scripts/fetch_models.py

fetch-datasets:
	python scripts/fetch_datasets.py

corpora:
	python scripts/build_corpora.py

calibrate:
	python scripts/calibrate.py

test:
	pytest tests/ -v

test-fast:
	pytest tests/unit tests/property tests/invariants -v

verify-invariants:
	pytest tests/invariants/ -v

lint:
	ruff check src/ tests/
	ruff format --check src/ tests/
	mypy src/

lint-fix:
	ruff check --fix src/ tests/
	ruff format src/ tests/

dev:
	uvicorn cleanroom.api.app:app --reload --host 0.0.0.0 --port 8000

web:
	cd web && npm install && npm run build

eval:
	python -m cleanroom.eval.harness

redteam:
	python -m cleanroom.redteam.evolve

demo:
	python -m cleanroom.api.demo

smoke-paypal:
	python scripts/paypal_smoke.py

smoke-mcp:
	python scripts/mcp_smoke.py

report:
	python -m cleanroom.eval.report

docker:
	docker build -t clean-room:latest .

docker-compose:
	docker-compose up --build

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/ 2>/dev/null || true
	rm -rf web/dist web/node_modules 2>/dev/null || true
	@echo "✓ Cleaned build artifacts"
