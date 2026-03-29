"""
autonomous-trader — main trading loop
Runs once per day (or on demand). Scans watchlist, generates Claude signals, executes trades.

Usage:
  python main.py             — normal run (skips if market closed)
  python main.py --dry-run   — test run, skips market check and order placement
"""
import sys
import time
from rich.console import Console
from rich.table import Table

from config.settings import WATCHLIST, MAX_DAILY_DRAWDOWN, STARTING_CAPITAL
from src.data.market import get_bars, get_latest_quote, compute_indicators
from src.data.news import get_news, TICKER_NAMES
from src.signals.claude_signal import generate_signal
from src.risk.sizing import position_size
from src.execution.broker import get_account, get_positions, place_order, close_position, is_market_open
from src.tracker.performance import record_snapshot, record_trade, compute_stats

console = Console()
DRY_RUN = "--dry-run" in sys.argv


def run_cycle():
    console.rule(f"[bold cyan]autonomous-trader {'[DRY RUN] ' if DRY_RUN else ''}cycle start")

    if not DRY_RUN and not is_market_open():
        console.print("[yellow]Market is closed. Skipping execution.[/yellow]")
        return

    account = get_account()
    portfolio_value = account["portfolio_value"]
    console.print(f"Portfolio: [green]${portfolio_value:,.2f}[/green]  Cash: ${account['cash']:,.2f}")

    # Daily drawdown guard
    drawdown = (STARTING_CAPITAL - portfolio_value) / STARTING_CAPITAL
    if drawdown > MAX_DAILY_DRAWDOWN:
        console.print(f"[red]Drawdown {drawdown:.1%} exceeds limit. Halting trading today.[/red]")
        return

    positions = get_positions()
    signals_table = Table(title="Signals", show_lines=True)
    signals_table.add_column("Symbol")
    signals_table.add_column("Action")
    signals_table.add_column("Confidence")
    signals_table.add_column("Reasoning")

    for symbol in WATCHLIST:
        try:
            # Fetch data
            bars = get_bars(symbol, days=60)
            bars = compute_indicators(bars)
            latest = get_latest_quote(symbol)
            news = get_news(symbol, TICKER_NAMES.get(symbol, symbol))

            last_row = bars.iloc[-1]
            indicators = {
                "price": latest["mid"],
                "sma_10": last_row.get("sma_10"),
                "sma_30": last_row.get("sma_30"),
                "rsi": last_row.get("rsi"),
                "atr": last_row.get("atr"),
                "pct_change": last_row.get("pct_change") * 100,
                "vol_zscore": last_row.get("vol_zscore"),
            }

            signal = generate_signal(symbol, indicators, news)
            action = signal["action"]
            confidence = signal["confidence"]
            reasoning = signal["reasoning"]

            signals_table.add_row(
                symbol,
                f"[green]{action}[/green]" if action == "buy" else f"[red]{action}[/red]" if action == "sell" else action,
                f"{confidence:.0%}",
                reasoning,
            )

            price = latest["mid"]

            if action == "buy" and symbol not in positions:
                qty = position_size(portfolio_value, price, confidence)
                if qty > 0:
                    if DRY_RUN:
                        console.print(f"[green][DRY RUN] Would BUY {qty}x {symbol} @ ${price:.2f}[/green]")
                    else:
                        result = place_order(symbol, qty, "buy")
                        record_trade(symbol, "buy", qty, price, confidence, reasoning)
                        console.print(f"[green]BUY {qty}x {symbol} @ ${price:.2f}[/green]  → {result['status']}")

            elif action == "sell" and symbol in positions:
                if DRY_RUN:
                    console.print(f"[red][DRY RUN] Would SELL {symbol}[/red]")
                else:
                    result = close_position(symbol)
                    record_trade(symbol, "sell", int(positions[symbol]["qty"]), price, confidence, reasoning)
                    console.print(f"[red]SELL {symbol}[/red]  → {result['status']}")

            time.sleep(1)  # rate limit

        except Exception as e:
            console.print(f"[yellow]Error processing {symbol}: {e}[/yellow]")

    console.print(signals_table)

    # Snapshot portfolio
    account = get_account()
    record_snapshot(account["portfolio_value"], account["cash"], get_positions())

    # Print stats
    stats = compute_stats()
    if stats:
        console.print(f"\n[bold]Performance[/bold]")
        console.print(f"  Total ROI:     [{'green' if stats['total_roi_pct'] >= 0 else 'red'}]{stats['total_roi_pct']:+.3f}%[/]")
        console.print(f"  Avg daily ROI: {stats['avg_daily_roi_pct']:+.3f}%")
        console.print(f"  Best day:      [green]{stats['best_day_pct']:+.3f}%[/green]")
        console.print(f"  Worst day:     [red]{stats['worst_day_pct']:+.3f}%[/red]")

    console.rule("[bold cyan]cycle complete")


if __name__ == "__main__":
    run_cycle()
