from config.settings import MAX_POSITION_SIZE


def kelly_fraction(confidence: float, win_loss_ratio: float = 1.5) -> float:
    """Kelly Criterion: f = (bp - q) / b where b=odds, p=win prob, q=loss prob."""
    p = confidence
    q = 1 - p
    b = win_loss_ratio
    fraction = (b * p - q) / b
    return max(0.0, min(fraction, MAX_POSITION_SIZE))


def position_size(portfolio_value: float, price: float, confidence: float) -> int:
    """Returns number of shares to buy given portfolio value and signal confidence."""
    fraction = kelly_fraction(confidence)
    dollar_amount = portfolio_value * fraction
    shares = int(dollar_amount / price)
    return max(0, shares)
