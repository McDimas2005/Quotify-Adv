.PHONY: dev-backend dev-frontend test build-index validate-models docker-build docker-run

dev-backend:
	cd backend && python app.py

dev-frontend:
	cd frontend && npm start

test:
	cd backend && pytest

build-index:
	cd backend && python scripts/build_sbert_index.py

validate-models:
	cd backend && python scripts/validate_models.py

docker-build:
	docker build -t quotify .

docker-run:
	docker run --rm -p 7860:7860 --env QUOTIFY_ENABLE_CROSS_ENCODER=false quotify

