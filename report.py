"""
report.py — run any time to see full week performance.
python report.py
"""
import json
import os
from datetime import datetime, date
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def load_json(path):
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def run():
    snapshots = load_json("logs/performance.json")
    trades = load_json("logs/trades.json")

    if not snapshots:
        console.print("[red]No performance data yet. Run the bot first.[/red]")
        return

    console.rule("[bold cyan]AUTONOMOUS TRADER — WEEKLY REPORT")

    # --- Portfolio summary ---
    start = snapshots[0]
    latest = snapshots[-1]
    starting_value = start["portfolio_value"]
    current_value = latest["portfolio_value"]
    total_roi = (current_value - starting_value) / starting_value * 100
    total_pnl = current_value - starting_value

    console.print(f"\n[bold]Portfolio Summary[/bold]")
    console.print(f"  Start:         ${starting_value:>12,.2f}")
    console.print(f"  Current:       ${current_value:>12,.2f}")
    color = "green" if total_pnl >= 0 else "red"
    console.print(f"  Total P&L:     [bold {color}]${total_pnl:>+12,.2f}[/bold {color}]")
    console.print(f"  Total ROI:     [bold {color}]{total_roi:>+.3f}%[/bold {color}]")

    # --- Daily breakdown ---
    by_day = defaultdict(list)
    for s in snapshots:
        day = s["timestamp"][:10]
        by_day[day].append(s["portfolio_value"])

    day_table = Table(title="Daily Performance", box=box.SIMPLE)
    day_table.add_column("Date")
    day_table.add_column("Open", justify="right")
    day_table.add_column("Close", justify="right")
    day_table.add_column("P&L", justify="right")
    day_table.add_column("ROI", justify="right")

    sorted_days = sorted(by_day.keys())
    for day in sorted_days:
        values = by_day[day]
        open_val = values[0]
        close_val = values[-1]
        pnl = close_val - open_val
        roi = (close_val - open_val) / open_val * 100
        color = "green" if pnl >= 0 else "red"
        day_table.add_row(
            day,
            f"${open_val:,.2f}",
            f"${close_val:,.2f}",
            f"[{color}]${pnl:+,.2f}[/{color}]",
            f"[{color}]{roi:+.3f}%[/{color}]",
        )
    console.print(day_table)

    # --- Trade log ---
    if trades:
        trade_table = Table(title=f"All Trades ({len(trades)} total)", box=box.SIMPLE)
        trade_table.add_column("Time")
        trade_table.add_column("Symbol")
        trade_table.add_column("Side")
        trade_table.add_column("Qty", justify="right")
        trade_table.add_column("Price", justify="right")
        trade_table.add_column("Value", justify="right")
        trade_table.add_column("Confidence", justify="right")
        trade_table.add_column("Reasoning")

        for t in trades[-50:]:  # last 50 trades
            color = "green" if t["side"] == "buy" else "red"
            trade_table.add_row(
                t["timestamp"][5:16],
                t["symbol"],
                f"[{color}]{t['side'].upper()}[/{color}]",
                str(t["qty"]),
                f"${t['price']:.2f}",
                f"${t['value']:,.0f}",
                f"{t['confidence']:.0%}",
                t["reasoning"][:60] + "..." if len(t["reasoning"]) > 60 else t["reasoning"],
            )
        console.print(trade_table)

        # --- Win/loss stats ---
        buys = {t["symbol"]: t for t in trades if t["side"] == "buy"}
        sells = [t for t in trades if t["side"] == "sell"]
        wins = sum(1 for s in sells if s.get("price", 0) > buys.get(s["symbol"], {}).get("price", 0))
        if sells:
            win_rate = wins / len(sells) * 100
            console.print(f"\n  Completed trades: {len(sells)}   Win rate: {win_rate:.1f}%")

    # --- Current positions ---
    if latest.get("positions"):
        pos_table = Table(title="Current Positions", box=box.SIMPLE)
        pos_table.add_column("Symbol")
        pos_table.add_column("Qty", justify="right")
        pos_table.add_column("Avg Entry", justify="right")
        pos_table.add_column("Market Value", justify="right")
        pos_table.add_column("Unrealized P&L", justify="right")
        pos_table.add_column("Return", justify="right")

        for sym, pos in latest["positions"].items():
            pnl = pos["unrealized_pl"]
            pct = float(pos["unrealized_plpc"]) * 100
            color = "green" if pnl >= 0 else "red"
            pos_table.add_row(
                sym,
                str(int(pos["qty"])),
                f"${pos['avg_entry']:.2f}",
                f"${pos['market_value']:,.2f}",
                f"[{color}]${pnl:+,.2f}[/{color}]",
                f"[{color}]{pct:+.2f}%[/{color}]",
            )
        console.print(pos_table)

    console.rule()


if __name__ == "__main__":
    run()
