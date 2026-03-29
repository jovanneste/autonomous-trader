from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from config.settings import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL

client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=True)


def get_account() -> dict:
    acct = client.get_account()
    return {
        "portfolio_value": float(acct.portfolio_value),
        "cash": float(acct.cash),
        "buying_power": float(acct.buying_power),
    }


def get_positions() -> dict:
    positions = client.get_all_positions()
    return {
        p.symbol: {
            "qty": float(p.qty),
            "avg_entry": float(p.avg_entry_price),
            "market_value": float(p.market_value),
            "unrealized_pl": float(p.unrealized_pl),
            "unrealized_plpc": float(p.unrealized_plpc),
        }
        for p in positions
    }


def place_order(symbol: str, qty: int, side: str) -> dict:
    if qty <= 0:
        return {"status": "skipped", "reason": "qty=0"}

    order_side = OrderSide.BUY if side == "buy" else OrderSide.SELL
    request = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=TimeInForce.DAY,
    )
    order = client.submit_order(request)
    return {
        "id": str(order.id),
        "symbol": order.symbol,
        "qty": order.qty,
        "side": str(order.side),
        "status": str(order.status),
    }


def close_position(symbol: str) -> dict:
    result = client.close_position(symbol)
    return {"status": "closed", "symbol": symbol, "order_id": str(result.id)}


def is_market_open() -> bool:
    clock = client.get_clock()
    return clock.is_open
