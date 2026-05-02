import pytest
from data_quality.checks import check_price_event, check_trade_event, validate_batch, QualityResult

@pytest.fixture
def valid_price_event():
    return {"event_id": "price_0_1234567890", "commodity": "Coffee, green", "country": "Brazil", "year": 2020, "price_usd_per_tonne": 1823.5, "currency": "USD", "source": "UN_FAO_SILVER"}

@pytest.fixture
def valid_trade_event():
    return {"event_id": "trade_1_1234567890", "commodity": "Cocoa beans", "country": "Ghana", "year": 2019, "trade_value_usd": 450000000.0, "element": "Export Value", "unit": "1000 US$", "source": "UN_FAO_SILVER"}

def test_valid_price_event_passes(valid_price_event):
    result = check_price_event(valid_price_event)
    assert result.passed is True

def test_valid_trade_event_passes(valid_trade_event):
    result = check_trade_event(valid_trade_event)
    assert result.passed is True

def test_price_event_fails_on_null_price(valid_price_event):
    valid_price_event["price_usd_per_tonne"] = None
    assert check_price_event(valid_price_event).passed is False

def test_price_event_fails_on_negative_price(valid_price_event):
    valid_price_event["price_usd_per_tonne"] = -100.0
    assert check_price_event(valid_price_event).passed is False

def test_price_event_fails_on_invalid_year(valid_price_event):
    valid_price_event["year"] = 1800
    assert check_price_event(valid_price_event).passed is False

def test_trade_event_fails_on_missing_field(valid_trade_event):
    del valid_trade_event["trade_value_usd"]
    assert check_trade_event(valid_trade_event).passed is False

def test_quality_result_pass_rate():
    result = QualityResult(passed=True, checks_run=5, checks_passed=5)
    assert result.pass_rate == 1.0

def test_validate_batch_summary(valid_price_event):
    bad = {**valid_price_event, "price_usd_per_tonne": None}
    summary = validate_batch([valid_price_event, valid_price_event, bad], event_type="price")
    assert summary["total"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1

def test_validate_empty_batch():
    summary = validate_batch([], event_type="price")
    assert summary["total"] == 0
    assert summary["pass_rate"] == 0.0
