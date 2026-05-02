# UN Agricultural Commodity Streaming Pipeline

![Pipeline CI](https://github.com/Toyor12/un-agri-commodity-streaming/actions/workflows/ci.yml/badge.svg)

Real-time streaming pipeline for UN FAO agricultural commodity data using Apache Kafka and PySpark Structured Streaming. Simulates live commodity price and trade feeds for coffee, cocoa and banana supply chains across 10 producer countries.

## Architecture
## Tech Stack

| Layer | Technology |
|---|---|
| Message Broker | Apache Kafka 7.5 (Confluent) |
| Stream Processing | PySpark 3.5 Structured Streaming |
| Producer | Python, kafka-python |
| Data Format | JSON (stream), Parquet (output) |
| Containerisation | Docker Compose |
| Data Quality | Custom validation framework |
| CI/CD | GitHub Actions |

## Quick Start

### Prerequisites
- Docker Desktop running
- Python 3.11
- Java 17

### Setup
```bash
make setup
make start
make test
```

### Stream Data
```bash
make stream-prices
make stream-trade
make stream-all
```

### Consume Stream
```bash
make consume
```

## Data Quality Checks

Each event is validated against 5 checks before reaching the gold layer:

| Check | Rule |
|---|---|
| Required fields | event_id, commodity, country, value, year must be non-null |
| Commodity validity | Must be Coffee, Cocoa or Bananas |
| Price range | Must be between 0 and 50,000 USD/tonne |
| Year range | Must be between 1990 and 2030 |
| Event ID | Must be non-empty with minimum length |

## Tests

14/14 tests passing covering producer event building, data quality checks and batch validation.

## Related Projects

- [un-agri-commodity-pipeline](https://github.com/Toyor12/un-agri-commodity-pipeline) — PySpark batch medallion pipeline
- [un-agri-commodity-dbt](https://github.com/Toyor12/un-agri-commodity-dbt) — dbt analytics engineering
