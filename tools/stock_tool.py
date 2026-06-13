"""
stock_tool.py
Fetches live financial data for NSE/BSE listed Indian companies using yfinance.
Includes formatted display fields and a curated ticker alias map to handle
demergers, similarly-named subsidiaries, and multi-exchange listings.
"""

import yfinance as yf
from yfinance import Search
from langchain_core.tools import tool


TICKER_ALIASES = {
    "tata motors": "TMCV.NS",
    "tata motors limited": "TMCV.NS",
    "tata motors commercial vehicles": "TMCV.NS",
    "infosys": "INFY.NS",
    "reliance": "RELIANCE.NS",
    "reliance industries": "RELIANCE.NS",
    "tcs": "TCS.NS",
    "tata consultancy services": "TCS.NS",
    "hdfc bank": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "state bank of india": "SBIN.NS",
    "sbi": "SBIN.NS",
    "wipro": "WIPRO.NS",
    "bharti airtel": "BHARTIARTL.NS",
    "itc": "ITC.NS",
    "larsen and toubro": "LT.NS",
    "l&t": "LT.NS",
    "axis bank": "AXISBANK.NS",
    "kotak mahindra bank": "KOTAKBANK.NS",
    "maruti suzuki": "MARUTI.NS",
    "bajaj finance": "BAJFINANCE.NS",
    "asian paints": "ASIANPAINT.NS",
    "hindustan unilever": "HINDUNILVR.NS",
    "sun pharma": "SUNPHARMA.NS",
    "adani enterprises": "ADANIENT.NS",
    "ntpc": "NTPC.NS",
    "power grid": "POWERGRID.NS",
    "ultratech cement": "ULTRACEMCO.NS",
    "titan": "TITAN.NS",
    "titan company": "TITAN.NS",
}


def _validate_ticker(symbol):
    """Checks if a ticker is valid and currently priced. Returns info dict or None."""
    try:
        info = yf.Ticker(symbol).info
        if info.get("currentPrice") is not None:
            return info
    except Exception:
        pass
    return None


def resolve_ticker(company_name: str) -> dict:
    """
    Takes a company name and returns the best-matching NSE/BSE ticker.

    Strategy:
    0. Check curated alias map first (validated before returning).
    1. Search and prefer .NS/.BO candidates whose name matches the search term.
    2. If no good .NS/.BO match, try constructing SYMBOL.NS from any
       name-matching EQUITY result and validate it.
    3. Fall back to first name-matching EQUITY, then first result overall.
    """
    normalized = company_name.lower().strip()
    if normalized in TICKER_ALIASES:
        symbol = TICKER_ALIASES[normalized]
        info = _validate_ticker(symbol)
        if info:
            return {
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "exchange": "NSI" if symbol.endswith(".NS") else "BSE",
            }

    search_result = Search(company_name, max_results=10)
    quotes = search_result.quotes

    if not quotes:
        return {"symbol": None, "name": None, "exchange": None}

    company_words = set(company_name.lower().split())

    def name_matches(candidate_name):
        if not candidate_name:
            return False
        candidate_words = set(candidate_name.lower().replace(".", "").split())
        overlap = company_words & candidate_words
        meaningful_overlap = overlap - {"limited", "ltd", "inc", "the", "and"}
        return len(meaningful_overlap) > 0

    for q in quotes:
        symbol = q.get("symbol", "")
        name = q.get("longname") or q.get("shortname") or ""
        if symbol.endswith(".NS") and name_matches(name):
            return {"symbol": symbol, "name": name, "exchange": q.get("exchange")}

    for q in quotes:
        symbol = q.get("symbol", "")
        name = q.get("longname") or q.get("shortname") or ""
        if symbol.endswith(".BO") and name_matches(name):
            return {"symbol": symbol, "name": name, "exchange": q.get("exchange")}

    for q in quotes:
        symbol = q.get("symbol", "")
        name = q.get("longname") or q.get("shortname") or ""
        quote_type = q.get("quoteType", "")

        if quote_type == "EQUITY" and name_matches(name) and "." in symbol:
            base_symbol = symbol.split(".")[0]
            candidate_ns = base_symbol + ".NS"
            info = _validate_ticker(candidate_ns)
            if info:
                return {
                    "symbol": candidate_ns,
                    "name": info.get("longName") or name,
                    "exchange": "NSI",
                }

    for q in quotes:
        name = q.get("longname") or q.get("shortname") or ""
        if q.get("quoteType") == "EQUITY" and name_matches(name):
            return {"symbol": q.get("symbol"), "name": name, "exchange": q.get("exchange")}

    first = quotes[0]
    return {
        "symbol": first.get("symbol"),
        "name": first.get("longname") or first.get("shortname"),
        "exchange": first.get("exchange"),
    }


def format_inr_crores(value):
    """Converts a raw rupee value to crores/lakh crores for readability."""
    if value is None:
        return "N/A"
    crores = value / 1e7
    if crores >= 1e5:
        return "₹" + format(crores / 1e5, ".2f") + " lakh crore"
    elif crores >= 1:
        return "₹" + format(crores, ".2f") + " crore"
    else:
        return "₹" + format(value, ",.2f")


def format_price(value):
    """Formats a price with Indian rupee symbol and comma separators."""
    if value is None:
        return "N/A"
    return "₹" + format(value, ",.2f")


def fetch_stock_data(company_name: str) -> dict:
    """
    Given a company name, resolves the ticker and fetches key financial data.
    Includes both raw numeric values and formatted display strings.
    """
    ticker_info = resolve_ticker(company_name)
    symbol = ticker_info["symbol"]

    if not symbol:
        return {"error": "Could not find a ticker for '" + company_name + "'"}

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        hist = ticker.history(period="3mo")
        if not hist.empty:
            price_3mo_ago = round(hist["Close"].iloc[0], 2)
            price_now = round(hist["Close"].iloc[-1], 2)
            momentum_pct = round(((price_now - price_3mo_ago) / price_3mo_ago) * 100, 2)
        else:
            momentum_pct = None

        current_price = info.get("currentPrice")
        market_cap = info.get("marketCap")
        week_high = info.get("fiftyTwoWeekHigh")
        week_low = info.get("fiftyTwoWeekLow")
        dividend_yield = info.get("dividendYield")
        pe_ratio = info.get("trailingPE")
        beta = info.get("beta")

        return {
            "symbol": symbol,
            "company_name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),

            "current_price_display": format_price(current_price),
            "market_cap_display": format_inr_crores(market_cap),
            "52_week_range_display": format_price(week_low) + " - " + format_price(week_high),
            "dividend_yield_display": (format(dividend_yield, ".2f") + "%") if dividend_yield else "N/A",

            "current_price": current_price,
            "market_cap": market_cap,
            "pe_ratio": round(pe_ratio, 2) if pe_ratio else None,
            "eps": info.get("trailingEps"),
            "52_week_high": week_high,
            "52_week_low": week_low,
            "3_month_momentum_pct": momentum_pct,
            "dividend_yield": dividend_yield,
            "beta": round(beta, 2) if beta else None,
            "recommendation": info.get("recommendationKey"),
        }

    except Exception as e:
        return {"error": "Failed to fetch data for '" + symbol + "': " + str(e)}


@tool
def fetch_stock_data_tool(company_name: str) -> dict:
    """
    Fetches live financial data for an Indian (NSE/BSE) listed company.

    Use this tool when you need current stock price, market cap, PE ratio,
    EPS, 52-week high/low, dividend yield, beta, analyst recommendation,
    or 3-month price momentum for a company.

    Args:
        company_name: The name of the company (e.g. "Reliance Industries",
                       "Tata Consultancy Services", "HDFC Bank").

    Returns:
        A dictionary containing the company's key financial metrics
        (both raw values and formatted display strings),
        or an error message if the company could not be found.
    """
    return fetch_stock_data(company_name)
