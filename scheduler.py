"""
scheduler.py — run this Monday morning and leave it running all week.
Triggers a full trading cycle at 10:00 AM ET every weekday.
"""
import schedule
import time
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo
from rich.console import Console

console = Console()
ET = ZoneInfo("America/New_York")


def run_cycle():
    now = datetime.now(ET)
    if now.weekday() >= 5:  # Saturday=5, Sunday=6
        console.print(f"[yellow]{now.strftime('%A')} — market closed, skipping.[/yellow]")
        return

    console.print(f"\n[bold cyan]Triggering trading cycle at {now.strftime('%Y-%m-%d %H:%M ET')}[/bold cyan]")
    result = subprocess.run(["python", "main.py"], capture_output=False)
    if result.returncode != 0:
        console.print("[red]Cycle failed — check logs above.[/red]")


# Run at 10:00 AM ET daily (30 min after market open — avoids open volatility)
# March = EDT (UTC-4), so 10:00 ET = 14:00 UTC
schedule.every().day.at("14:00").do(run_cycle)

console.print("[bold green]Scheduler started.[/bold green]")
console.print("Trading cycles will run at 10:00 AM ET on weekdays.")
console.print("Leave this terminal open all week. Press Ctrl+C to stop.\n")

# Run once immediately on start so we don't wait until 10am
console.print("Running initial cycle now...")
run_cycle()

while True:
    schedule.run_pending()
    time.sleep(60)
