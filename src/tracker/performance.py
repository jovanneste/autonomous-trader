import json
import os
from datetime import datetime

LOG_FILE = "logs/performance.json"


def _load() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def _save(records: list):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "w") as f:
        json.dump(records, f, indent=2)


def record_snapshot(portfolio_value: float, cash: float, positions: dict):
    records = _load()
    records.append({
        "timestamp": datetime.utcnow().isoformat(),
        "portfolio_value": portfolio_value,
        "cash": cash,
        "positions": positions,
    })
    _save(records)


def record_trade(symbol: str, side: str, qty: int, price: float, confidence: float, reasoning: str):
    path = "logs/trades.json"
    trades = []
    if os.path.exists(path):
        with open(path) as f:
            trades = json.load(f)
    trades.append({
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "side": side,
        "qty": qty,
        "price": price,
        "confidence": confidence,
        "reasoning": reasoning,
        "value": qty * price,
    })
    os.makedirs("logs", exist_ok=True)
    with open(path, "w") as f:
        json.dump(trades, f, indent=2)


def compute_stats() -> dict:
    records = _load()
    if len(records) < 2:
        return {}

    starting = records[0]["portfolio_value"]
    current = records[-1]["portfolio_value"]
    total_roi = (current - starting) / starting * 100

    # Daily ROI
    daily = []
    for i in range(1, len(records)):
        prev = records[i - 1]["portfolio_value"]
        curr = records[i]["portfolio_value"]
        daily.append((curr - prev) / prev * 100)

    return {
        "starting_value": starting,
        "current_value": current,
        "total_roi_pct": round(total_roi, 3),
        "avg_daily_roi_pct": round(sum(daily) / len(daily), 3) if daily else 0,
        "best_day_pct": round(max(daily), 3) if daily else 0,
        "worst_day_pct": round(min(daily), 3) if daily else 0,
        "snapshots": len(records),
    }
