.PHONY: data all test clean

data:
	bash scripts/download_data.sh

all:
	python -m src.pipeline

test:
	python -m pytest -q

clean:
	rm -rf data/processed/*.parquet outputs/tables/*.csv outputs/key_numbers.json
