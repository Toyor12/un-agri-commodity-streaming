import json
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path
import pandas as pd
from kafka import KafkaProducer
from kafka.errors import KafkaError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
PRICES_TOPIC = "commodity-prices"
TRADE_TOPIC = "commodity-trade"

def create_producer(bootstrap_servers):
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
        acks="all", retries=3, max_block_ms=10000,
    )

def load_silver_data(data_path):
    base = Path(data_path)
    prices_df = pd.read_parquet(base / "prices")
    trade_df = pd.read_parquet(base / "trade")
    logger.info(f"Loaded {len(prices_df)} price records and {len(trade_df)} trade records")
    return prices_df, trade_df

def build_price_event(row):
    return {
        "event_id": f"price_{row.name}_{int(time.time() * 1000)}",
        "event_type": "commodity_price_update",
        "timestamp": datetime.utcnow().isoformat(),
        "commodity": str(row.get("Item", "Unknown")),
        "country": str(row.get("Area", "Unknown")),
        "year": int(row["Year"]) if pd.notna(row.get("Year")) else None,
        "price_usd_per_tonne": float(row["Value"]) if pd.notna(row.get("Value")) else None,
        "currency": "USD",
        "source": "UN_FAO_SILVER",
        "ingested_at": datetime.utcnow().isoformat(),
    }

def build_trade_event(row):
    return {
        "event_id": f"trade_{row.name}_{int(time.time() * 1000)}",
        "event_type": "commodity_trade_update",
        "timestamp": datetime.utcnow().isoformat(),
        "commodity": str(row.get("Item", "Unknown")),
        "country": str(row.get("Area", "Unknown")),
        "year": int(row["Year"]) if pd.notna(row.get("Year")) else None,
        "trade_value_usd": float(row["Value"]) if pd.notna(row.get("Value")) else None,
        "element": str(row.get("Element", "Unknown")),
        "unit": str(row.get("Unit", "Unknown")),
        "source": "UN_FAO_SILVER",
        "ingested_at": datetime.utcnow().isoformat(),
    }

def stream_prices(producer, prices_df, delay_ms=100, max_records=None):
    sent = 0
    sample = prices_df.head(max_records) if max_records else prices_df
    for idx, row in sample.iterrows():
        try:
            event = build_price_event(row)
            key = f"{event['commodity']}_{event['country']}"
            producer.send(PRICES_TOPIC, key=key, value=event).get(timeout=10)
            sent += 1
            if sent % 100 == 0:
                logger.info(f"Sent {sent} price events")
            time.sleep(delay_ms / 1000)
        except KafkaError as e:
            logger.error(f"Failed to send price event {idx}: {e}")
    producer.flush()
    return sent

def stream_trade(producer, trade_df, delay_ms=100, max_records=None):
    sent = 0
    sample = trade_df.head(max_records) if max_records else trade_df
    for idx, row in sample.iterrows():
        try:
            event = build_trade_event(row)
            key = f"{event['commodity']}_{event['country']}"
            producer.send(TRADE_TOPIC, key=key, value=event).get(timeout=10)
            sent += 1
            if sent % 100 == 0:
                logger.info(f"Sent {sent} trade events")
            time.sleep(delay_ms / 1000)
        except KafkaError as e:
            logger.error(f"Failed to send trade event {idx}: {e}")
    producer.flush()
    return sent

def main():
    parser = argparse.ArgumentParser(description="UN FAO Commodity Stream Producer")
    parser.add_argument("--data-path", default=str(Path.home() / "un-agri-commodity-pipeline/data/silver"))
    parser.add_argument("--delay-ms", type=int, default=100)
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--topic", choices=["prices", "trade", "both"], default="both")
    args = parser.parse_args()
    prices_df, trade_df = load_silver_data(args.data_path)
    producer = create_producer(KAFKA_BOOTSTRAP_SERVERS)
    try:
        if args.topic in ("prices", "both"):
            stream_prices(producer, prices_df, args.delay_ms, args.max_records)
        if args.topic in ("trade", "both"):
            stream_trade(producer, trade_df, args.delay_ms, args.max_records)
    finally:
        producer.close()

if __name__ == "__main__":
    main()
