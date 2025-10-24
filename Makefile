
.PHONY: help install test run docker-build docker-run clean lint format

help:
	@echo "Comandos disponíveis:"
	@echo "  make install       - Instala dependências"
	@echo "  make test          - Executa testes"
	@echo "  make test-cov      - Executa testes com cobertura"
	@echo "  make run           - Executa aplicação localmente"
	@echo "  make docker-build  - Build da imagem Docker"
	@echo "  make docker-run    - Executa container Docker"
	@echo "  make docker-up     - Inicia com docker-compose"
	@echo "  make docker-down   - Para docker-compose"
	@echo "  make clean         - Remove arquivos temporários"
	@echo "  make lint          - Executa linting"
	@echo "  make format        - Formata código"

install:
	pip install -r requirements.txt

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

run:
	python app.py

docker-build:
	docker build -t deviation-classifier-api .

docker-run:
	docker run -p 8000:8000 --env-file .env deviation-classifier-api

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage

lint:
	@echo "Linting com flake8..."
	@pip install flake8 > /dev/null 2>&1 || true
	@flake8 app tests --max-line-length=100 --ignore=E501 || true

format:
	@echo "Formatando com black..."
	@pip install black > /dev/null 2>&1 || true
	@black app tests || true

create-model:
	python create_mock_model.py

dev:
	@echo "Iniciando em modo desenvolvimento..."
	export DEBUG=true && python app.py
