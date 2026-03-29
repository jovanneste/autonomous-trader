import os
from dotenv import load_dotenv

load_dotenv()

# Alpaca
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# News
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Trading parameters
STARTING_CAPITAL = 500.0
MAX_POSITION_SIZE = 0.10       # max 10% of portfolio per trade
MAX_DAILY_DRAWDOWN = 0.05      # stop trading if down 5% in a day
MIN_SIGNAL_CONFIDENCE = 0.65   # Claude must be >= 65% confident to trade

# Universe of tradeable symbols (top 100)
WATCHLIST = [
    # Mega-cap tech
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO", "ORCL",
    # Tech
    "AMD", "INTC", "QCOM", "CRM", "ADBE", "NOW", "IBM", "TXN", "MU", "AMAT",
    "LRCX", "KLAC", "ADI", "MRVL", "PANW", "SNPS", "CDNS", "FTNT", "ANSS", "TEAM",
    # Finance
    "BRK.B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "BLK", "AXP",
    "C", "SCHW", "SPGI", "ICE", "CME",
    # Healthcare
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "DHR", "PFE", "AMGN",
    "ISRG", "BSX", "REGN", "VRTX", "GILD",
    # Consumer
    "WMT", "COST", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW", "TJX", "PG",
    "KO", "PEP", "PM", "MO", "CL",
    # Media / Entertainment
    "NFLX", "DIS", "CMCSA", "CHTR", "WBD",
    # Energy
    "XOM", "CVX", "COP", "EOG", "SLB",
    # Industrial
    "CAT", "DE", "BA", "GE", "HON", "LMT", "RTX", "UPS", "FDX", "ETN",
    # ETFs (broad market signals)
    "SPY", "QQQ", "IWM", "XLK", "XLF", "XLE", "XLV", "GLD",
    # High-momentum / meme adjacent
    "PLTR", "COIN", "HOOD", "RBLX", "SNAP", "UBER", "LYFT", "ABNB", "DASH", "ROKU",
]
