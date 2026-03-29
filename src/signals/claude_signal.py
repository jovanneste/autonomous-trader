import json
import subprocess
from config.settings import MIN_SIGNAL_CONFIDENCE


def generate_signal(symbol: str, indicators: dict, news: list[dict]) -> dict:
    """
    Use Claude CLI to reason about a trade signal.
    Returns: {action: 'buy'|'sell'|'hold', confidence: float, reasoning: str}
    """
    news_text = "\n".join(
        f"- [{a['source']}] {a['title']}: {a['description']}"
        for a in news[:5]
    ) or "No recent news."

    prompt = f"""You are a quantitative trading analyst. Analyze the following data for {symbol} and decide whether to BUY, SELL, or HOLD.

## Technical Indicators
- Current price: ${indicators.get('price', 'N/A')}
- SMA 10: {indicators.get('sma_10', 'N/A'):.2f}
- SMA 30: {indicators.get('sma_30', 'N/A'):.2f}
- RSI (14): {indicators.get('rsi', 'N/A'):.1f}
- ATR (14): {indicators.get('atr', 'N/A'):.2f}
- 1-day % change: {indicators.get('pct_change', 'N/A'):.2f}%
- Volume z-score: {indicators.get('vol_zscore', 'N/A'):.2f} (>2 = unusual volume)

## Recent News (last 24h)
{news_text}

## Instructions
Respond in JSON only. No markdown, no code blocks, just raw JSON. Format:
{{"action": "buy" or "sell" or "hold", "confidence": <float 0.0-1.0>, "reasoning": "<1-2 sentence explanation>"}}

Rules:
- Only recommend buy/sell if confidence >= 0.65, otherwise hold
- RSI > 70 = overbought, RSI < 30 = oversold
- Positive news + upward momentum = bullish signal
- Be conservative: missing a trade is better than a bad trade
"""

    result = subprocess.run(
        ["claude", "-p", prompt],
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error: {result.stderr}")

    raw = result.stdout.strip()

    # Strip markdown code blocks if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    parsed = json.loads(raw)

    if parsed["confidence"] < MIN_SIGNAL_CONFIDENCE:
        parsed["action"] = "hold"

    return parsed
