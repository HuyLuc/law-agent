.PHONY: ingest index test eval up down

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
