import requests
from datetime import datetime, timedelta
from config.settings import NEWS_API_KEY

TICKER_NAMES = {
    "AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "Nvidia", "TSLA": "Tesla",
    "AMZN": "Amazon", "META": "Meta", "GOOGL": "Google", "GOOG": "Google Alphabet",
    "AMD": "AMD", "INTC": "Intel", "QCOM": "Qualcomm", "CRM": "Salesforce",
    "ADBE": "Adobe", "NOW": "ServiceNow", "IBM": "IBM", "TXN": "Texas Instruments",
    "MU": "Micron", "AMAT": "Applied Materials", "LRCX": "Lam Research",
    "AVGO": "Broadcom", "ORCL": "Oracle", "KLAC": "KLA Corp", "ADI": "Analog Devices",
    "MRVL": "Marvell", "PANW": "Palo Alto Networks", "SNPS": "Synopsys",
    "CDNS": "Cadence", "FTNT": "Fortinet", "ANSS": "Ansys", "TEAM": "Atlassian",
    "BRK.B": "Berkshire Hathaway", "JPM": "JPMorgan", "V": "Visa", "MA": "Mastercard",
    "BAC": "Bank of America", "WFC": "Wells Fargo", "GS": "Goldman Sachs",
    "MS": "Morgan Stanley", "BLK": "BlackRock", "AXP": "American Express",
    "C": "Citigroup", "SCHW": "Charles Schwab", "SPGI": "S&P Global",
    "ICE": "Intercontinental Exchange", "CME": "CME Group",
    "LLY": "Eli Lilly", "UNH": "UnitedHealth", "JNJ": "Johnson Johnson",
    "ABBV": "AbbVie", "MRK": "Merck", "TMO": "Thermo Fisher", "ABT": "Abbott",
    "DHR": "Danaher", "PFE": "Pfizer", "AMGN": "Amgen", "ISRG": "Intuitive Surgical",
    "BSX": "Boston Scientific", "REGN": "Regeneron", "VRTX": "Vertex", "GILD": "Gilead",
    "WMT": "Walmart", "COST": "Costco", "HD": "Home Depot", "MCD": "McDonald's",
    "NKE": "Nike", "SBUX": "Starbucks", "TGT": "Target", "LOW": "Lowe's",
    "TJX": "TJX Companies", "PG": "Procter Gamble", "KO": "Coca-Cola",
    "PEP": "PepsiCo", "PM": "Philip Morris", "MO": "Altria", "CL": "Colgate",
    "NFLX": "Netflix", "DIS": "Disney", "CMCSA": "Comcast", "CHTR": "Charter",
    "WBD": "Warner Bros Discovery", "XOM": "Exxon", "CVX": "Chevron",
    "COP": "ConocoPhillips", "EOG": "EOG Resources", "SLB": "Schlumberger",
    "CAT": "Caterpillar", "DE": "John Deere", "BA": "Boeing", "GE": "GE Aerospace",
    "HON": "Honeywell", "LMT": "Lockheed Martin", "RTX": "Raytheon", "UPS": "UPS",
    "FDX": "FedEx", "ETN": "Eaton",
    "SPY": "S&P 500 ETF", "QQQ": "Nasdaq ETF", "IWM": "Russell 2000 ETF",
    "XLK": "Technology ETF", "XLF": "Financial ETF", "XLE": "Energy ETF",
    "XLV": "Healthcare ETF", "GLD": "Gold ETF",
    "PLTR": "Palantir", "COIN": "Coinbase", "HOOD": "Robinhood", "RBLX": "Roblox",
    "SNAP": "Snapchat", "UBER": "Uber", "LYFT": "Lyft", "ABNB": "Airbnb",
    "DASH": "DoorDash", "ROKU": "Roku",
}


def get_news(symbol: str, company_name: str = "", hours: int = 24) -> list[dict]:
    query = company_name if company_name else symbol
    from_time = (datetime.utcnow() - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%S")
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": f"{query} stock",
        "from": from_time,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY,
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    return [
        {
            "title": a["title"],
            "description": a.get("description", ""),
            "published_at": a["publishedAt"],
            "source": a["source"]["name"],
        }
        for a in articles
        if a.get("title") and "[Removed]" not in a.get("title", "")
    ]
