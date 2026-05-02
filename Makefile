.PHONY: start stop test lint setup clean

setup:
	pip install -r producer/requirements.txt
	pip install -r consumer/requirements.txt
	pip install pytest pytest-cov flake8

start:
	docker-compose up -d
	@echo "Kafka UI available at http://localhost:8080"
	sleep 15

stop:
	docker-compose down

restart: stop start

stream-prices:
	PYTHONPATH=. python producer/producer.py --topic prices --delay-ms 50 --max-records 500

stream-trade:
	PYTHONPATH=. python producer/producer.py --topic trade --delay-ms 50 --max-records 500

stream-all:
	PYTHONPATH=. python producer/producer.py --topic both --delay-ms 50

consume:
	PYTHONPATH=. python consumer/consumer.py

test:
	PYTHONPATH=. pytest tests/ -v --tb=short --cov=producer --cov=data_quality --cov-report=term-missing

lint:
	flake8 producer/ consumer/ data_quality/ tests/ --max-line-length=120 --ignore=E501,W503

clean:
	docker-compose down -v
	rm -rf checkpoints/
	rm -rf data/gold/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
