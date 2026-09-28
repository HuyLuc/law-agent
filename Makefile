.PHONY: ingest index test eval up down docker-index

ingest:
	python -m src.ingestion.parser

index:
	python -m src.ingestion.index_qdrant

test:
	pytest

eval:
	python -m eval.run_generation_eval

up:
	docker compose up -d

down:
	docker compose down

docker-index:
	docker compose exec api python -m src.ingestion.index_qdrant
