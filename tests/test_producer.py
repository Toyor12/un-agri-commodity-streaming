import pytest
import time
from unittest.mock import MagicMock
from producer.producer import build_price_event, build_trade_event

def make_row(data, name=0):
    row = MagicMock()
    row.name = name
    row.get = lambda key, default=None: data.get(key, default)
    row.__getitem__ = lambda self, key: data[key]
    return row

def test_build_price_event_structure():
    row = make_row({"Item": "Coffee, green", "Area": "Brazil", "Year": 2020, "Value": 1823.5})
    event = build_price_event(row)
    assert "event_id" in event
    assert "commodity" in event
    assert "price_usd_per_tonne" in event
    assert "year" in event
    assert "source" in event

def test_build_price_event_values():
    row = make_row({"Item": "Coffee, green", "Area": "Brazil", "Year": 2020, "Value": 1823.5})
    event = build_price_event(row)
    assert event["commodity"] == "Coffee, green"
    assert event["country"] == "Brazil"
    assert event["year"] == 2020
    assert event["price_usd_per_tonne"] == 1823.5
    assert event["source"] == "UN_FAO_SILVER"
    assert event["currency"] == "USD"

def test_build_trade_event_values():
    row = make_row({"Item": "Cocoa beans", "Area": "Ghana", "Year": 2019, "Value": 450000000.0, "Element": "Export Value", "Unit": "1000 US$"}, name=1)
    event = build_trade_event(row)
    assert event["commodity"] == "Cocoa beans"
    assert event["country"] == "Ghana"
    assert event["year"] == 2019
    assert event["trade_value_usd"] == 450000000.0

def test_price_event_id_is_unique():
    row = make_row({"Item": "Coffee, green", "Area": "Brazil", "Year": 2020, "Value": 1823.5})
    event1 = build_price_event(row)
    time.sleep(0.01)
    event2 = build_price_event(row)
    assert event1["event_id"] != event2["event_id"]

def test_build_price_event_handles_null_value():
    row = make_row({"Item": "Bananas", "Area": "Ecuador", "Year": 2021, "Value": None}, name=2)
    event = build_price_event(row)
    assert event["price_usd_per_tonne"] is None
