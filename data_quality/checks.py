import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

VALID_COMMODITIES = {"Coffee", "Cocoa", "Bananas"}
PRICE_MIN_USD = 0.0
PRICE_MAX_USD = 50000.0
YEAR_MIN = 1990
YEAR_MAX = 2030

@dataclass
class QualityResult:
    passed: bool
    checks_run: int = 0
    checks_passed: int = 0
    failures: list = field(default_factory=list)

    @property
    def pass_rate(self):
        if self.checks_run == 0:
            return 0.0
        return self.checks_passed / self.checks_run

def check_price_event(event):
    failures = []
    checks_run = 0
    checks_passed = 0

    checks_run += 1
    required = ["event_id", "commodity", "country", "price_usd_per_tonne", "year"]
    missing = [f for f in required if event.get(f) is None]
    if missing:
        failures.append(f"Missing required fields: {missing}")
    else:
        checks_passed += 1

    checks_run += 1
    commodity = event.get("commodity", "")
    if any(c.lower() in commodity.lower() for c in VALID_COMMODITIES):
        checks_passed += 1
    else:
        failures.append(f"Invalid commodity: {commodity}")

    checks_run += 1
    price = event.get("price_usd_per_tonne")
    if price is not None:
        if PRICE_MIN_USD <= float(price) <= PRICE_MAX_USD:
            checks_passed += 1
        else:
            failures.append(f"Price {price} out of range")
    else:
        failures.append("Price is null")

    checks_run += 1
    year = event.get("year")
    if year is not None:
        if YEAR_MIN <= int(year) <= YEAR_MAX:
            checks_passed += 1
        else:
            failures.append(f"Year {year} out of range")
    else:
        failures.append("Year is null")

    checks_run += 1
    event_id = event.get("event_id", "")
    if event_id and len(event_id) >= 5:
        checks_passed += 1
    else:
        failures.append(f"Invalid event_id: {event_id}")

    return QualityResult(passed=len(failures)==0, checks_run=checks_run, checks_passed=checks_passed, failures=failures)

def check_trade_event(event):
    failures = []
    checks_run = 0
    checks_passed = 0

    checks_run += 1
    required = ["event_id", "commodity", "country", "trade_value_usd", "year"]
    missing = [f for f in required if event.get(f) is None]
    if missing:
        failures.append(f"Missing required fields: {missing}")
    else:
        checks_passed += 1

    checks_run += 1
    commodity = event.get("commodity", "")
    if any(c.lower() in commodity.lower() for c in VALID_COMMODITIES):
        checks_passed += 1
    else:
        failures.append(f"Invalid commodity: {commodity}")

    checks_run += 1
    trade_value = event.get("trade_value_usd")
    if trade_value is not None:
        if float(trade_value) >= 0:
            checks_passed += 1
        else:
            failures.append(f"Negative trade value: {trade_value}")
    else:
        failures.append("Trade value is null")

    checks_run += 1
    year = event.get("year")
    if year is not None:
        if YEAR_MIN <= int(year) <= YEAR_MAX:
            checks_passed += 1
        else:
            failures.append(f"Year {year} out of range")
    else:
        failures.append("Year is null")

    checks_run += 1
    element = event.get("element", "")
    if element:
        checks_passed += 1
    else:
        failures.append("Element field is empty")

    return QualityResult(passed=len(failures)==0, checks_run=checks_run, checks_passed=checks_passed, failures=failures)

def validate_batch(events, event_type="price"):
    check_fn = check_price_event if event_type == "price" else check_trade_event
    results = [check_fn(e) for e in events]
    passed = sum(1 for r in results if r.passed)
    return {
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": passed / len(results) if results else 0.0,
        "failure_details": [{"index": i, "failures": r.failures} for i, r in enumerate(results) if not r.passed]
    }
