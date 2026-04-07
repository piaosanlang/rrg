from typing import Dict, List, Any, Optional
import math


BENCHMARK = "SPY"

RS_EMA_PERIOD = 10
MOM_EMA_PERIOD = 5
NORM_WINDOW = 39
TAIL_LENGTH = 12
ZSCORE_SCALE = 6

SECTORS = [
    {"ticker": "XLK",  "name": "Technology",      "color": "#00d4ff"},
    {"ticker": "XLF",  "name": "Financials",       "color": "#f59e0b"},
    {"ticker": "XLV",  "name": "Health Care",      "color": "#10b981"},
    {"ticker": "XLE",  "name": "Energy",           "color": "#f97316"},
    {"ticker": "XLI",  "name": "Industrials",      "color": "#8b5cf6"},
    {"ticker": "XLY",  "name": "Cons. Discret.",   "color": "#ec4899"},
    {"ticker": "XLP",  "name": "Cons. Staples",    "color": "#06b6d4"},
    {"ticker": "XLU",  "name": "Utilities",        "color": "#84cc16"},
    {"ticker": "XLRE", "name": "Real Estate",      "color": "#f43f5e"},
    {"ticker": "XLB",  "name": "Materials",        "color": "#a78bfa"},
    {"ticker": "XLC",  "name": "Comm. Services",   "color": "#fb923c"},
]

SECTOR_HOLDINGS: Dict[str, List[Dict[str, str]]] = {
    "XLK": [
        {"ticker": "AAPL",  "name": "Apple",           "color": "#00d4ff"},
        {"ticker": "MSFT",  "name": "Microsoft",       "color": "#f59e0b"},
        {"ticker": "NVDA",  "name": "Nvidia",          "color": "#10b981"},
        {"ticker": "AVGO",  "name": "Broadcom",        "color": "#f97316"},
        {"ticker": "AMD",   "name": "AMD",             "color": "#8b5cf6"},
        {"ticker": "ORCL",  "name": "Oracle",          "color": "#ec4899"},
        {"ticker": "ADBE",  "name": "Adobe",           "color": "#06b6d4"},
        {"ticker": "CSCO",  "name": "Cisco",           "color": "#84cc16"},
        {"ticker": "ACN",   "name": "Accenture",       "color": "#f43f5e"},
        {"ticker": "PLTR",  "name": "Palantir",        "color": "#a78bfa"},
    ],
    "XLF": [
        {"ticker": "BRK-B", "name": "Berkshire",       "color": "#00d4ff"},
        {"ticker": "JPM",   "name": "JPMorgan",        "color": "#f59e0b"},
        {"ticker": "V",     "name": "Visa",            "color": "#10b981"},
        {"ticker": "MA",    "name": "Mastercard",      "color": "#f97316"},
        {"ticker": "BAC",   "name": "Bank of America", "color": "#8b5cf6"},
        {"ticker": "GS",    "name": "Goldman Sachs",   "color": "#ec4899"},
        {"ticker": "WFC",   "name": "Wells Fargo",     "color": "#06b6d4"},
        {"ticker": "C",     "name": "Citigroup",       "color": "#84cc16"},
        {"ticker": "MS",    "name": "Morgan Stanley",  "color": "#f43f5e"},
        {"ticker": "AXP",   "name": "Amex",            "color": "#a78bfa"},
    ],
    "XLV": [
        {"ticker": "LLY",   "name": "Eli Lilly",       "color": "#00d4ff"},
        {"ticker": "UNH",   "name": "UnitedHealth",    "color": "#f59e0b"},
        {"ticker": "JNJ",   "name": "Johnson",         "color": "#10b981"},
        {"ticker": "ABBV",  "name": "AbbVie",          "color": "#f97316"},
        {"ticker": "MRK",   "name": "Merck",           "color": "#8b5cf6"},
        {"ticker": "TMO",   "name": "Thermo Fisher",   "color": "#ec4899"},
        {"ticker": "ABT",   "name": "Abbott",          "color": "#06b6d4"},
        {"ticker": "DHR",   "name": "Danaher",         "color": "#84cc16"},
        {"ticker": "PFE",   "name": "Pfizer",          "color": "#f43f5e"},
        {"ticker": "AMGN",  "name": "Amgen",           "color": "#a78bfa"},
    ],
    "XLE": [
        {"ticker": "XOM",   "name": "ExxonMobil",      "color": "#00d4ff"},
        {"ticker": "CVX",   "name": "Chevron",         "color": "#f59e0b"},
        {"ticker": "COP",   "name": "ConocoPhillips",  "color": "#10b981"},
        {"ticker": "EOG",   "name": "EOG Resources",   "color": "#f97316"},
        {"ticker": "SLB",   "name": "Schlumberger",    "color": "#8b5cf6"},
        {"ticker": "MPC",   "name": "Marathon",        "color": "#ec4899"},
        {"ticker": "PXD",   "name": "Pioneer",         "color": "#06b6d4"},
        {"ticker": "VLO",   "name": "Valero",          "color": "#84cc16"},
        {"ticker": "PSX",   "name": "Phillips 66",     "color": "#f43f5e"},
        {"ticker": "OXY",   "name": "Occidental",      "color": "#a78bfa"},
    ],
    "XLI": [
        {"ticker": "GE",    "name": "GE Aerospace",    "color": "#00d4ff"},
        {"ticker": "CAT",   "name": "Caterpillar",     "color": "#f59e0b"},
        {"ticker": "RTX",   "name": "RTX Corp",        "color": "#10b981"},
        {"ticker": "HON",   "name": "Honeywell",       "color": "#f97316"},
        {"ticker": "UNP",   "name": "Union Pacific",   "color": "#8b5cf6"},
        {"ticker": "LMT",   "name": "Lockheed",        "color": "#ec4899"},
        {"ticker": "DE",    "name": "Deere",           "color": "#06b6d4"},
        {"ticker": "BA",    "name": "Boeing",          "color": "#84cc16"},
        {"ticker": "MMM",   "name": "3M",              "color": "#f43f5e"},
        {"ticker": "ETN",   "name": "Eaton",           "color": "#a78bfa"},
    ],
    "XLY": [
        {"ticker": "AMZN",  "name": "Amazon",          "color": "#00d4ff"},
        {"ticker": "TSLA",  "name": "Tesla",           "color": "#f59e0b"},
        {"ticker": "HD",    "name": "Home Depot",      "color": "#10b981"},
        {"ticker": "MCD",   "name": "McDonald's",      "color": "#f97316"},
        {"ticker": "NKE",   "name": "Nike",            "color": "#8b5cf6"},
        {"ticker": "LOW",   "name": "Lowe's",          "color": "#ec4899"},
        {"ticker": "SBUX",  "name": "Starbucks",       "color": "#06b6d4"},
        {"ticker": "TJX",   "name": "TJX",             "color": "#84cc16"},
        {"ticker": "BKNG",  "name": "Booking",         "color": "#f43f5e"},
        {"ticker": "CMG",   "name": "Chipotle",        "color": "#a78bfa"},
    ],
    "XLP": [
        {"ticker": "PG",    "name": "Procter Gamble",  "color": "#00d4ff"},
        {"ticker": "KO",    "name": "Coca-Cola",       "color": "#f59e0b"},
        {"ticker": "PEP",   "name": "PepsiCo",         "color": "#10b981"},
        {"ticker": "COST",  "name": "Costco",          "color": "#f97316"},
        {"ticker": "WMT",   "name": "Walmart",         "color": "#8b5cf6"},
        {"ticker": "PM",    "name": "Philip Morris",   "color": "#ec4899"},
        {"ticker": "MO",    "name": "Altria",          "color": "#06b6d4"},
        {"ticker": "CL",    "name": "Colgate",         "color": "#84cc16"},
        {"ticker": "MDLZ",  "name": "Mondelez",        "color": "#f43f5e"},
        {"ticker": "STZ",   "name": "Constellation",   "color": "#a78bfa"},
    ],
    "XLU": [
        {"ticker": "NEE",   "name": "NextEra",         "color": "#00d4ff"},
        {"ticker": "SO",    "name": "Southern Co",     "color": "#f59e0b"},
        {"ticker": "DUK",   "name": "Duke Energy",     "color": "#10b981"},
        {"ticker": "AEP",   "name": "AEP",             "color": "#f97316"},
        {"ticker": "SRE",   "name": "Sempra",          "color": "#8b5cf6"},
        {"ticker": "D",     "name": "Dominion",        "color": "#ec4899"},
        {"ticker": "EXC",   "name": "Exelon",          "color": "#06b6d4"},
        {"ticker": "XEL",   "name": "Xcel Energy",     "color": "#84cc16"},
        {"ticker": "ED",    "name": "Con Edison",      "color": "#f43f5e"},
        {"ticker": "WEC",   "name": "WEC Energy",      "color": "#a78bfa"},
    ],
    "XLRE": [
        {"ticker": "PLD",   "name": "Prologis",        "color": "#00d4ff"},
        {"ticker": "AMT",   "name": "American Tower",  "color": "#f59e0b"},
        {"ticker": "EQIX",  "name": "Equinix",         "color": "#10b981"},
        {"ticker": "CCI",   "name": "Crown Castle",    "color": "#f97316"},
        {"ticker": "PSA",   "name": "Public Storage",  "color": "#8b5cf6"},
        {"ticker": "O",     "name": "Realty Income",   "color": "#ec4899"},
        {"ticker": "WELL",  "name": "Welltower",       "color": "#06b6d4"},
        {"ticker": "SPG",   "name": "Simon Property",  "color": "#84cc16"},
        {"ticker": "DLR",   "name": "Digital Realty",  "color": "#f43f5e"},
        {"ticker": "EXR",   "name": "Extra Space",     "color": "#a78bfa"},
    ],
    "XLB": [
        {"ticker": "LIN",   "name": "Linde",           "color": "#00d4ff"},
        {"ticker": "SHW",   "name": "Sherwin-Williams", "color": "#f59e0b"},
        {"ticker": "FCX",   "name": "Freeport-McMoRan", "color": "#10b981"},
        {"ticker": "NEM",   "name": "Newmont",         "color": "#f97316"},
        {"ticker": "NUE",   "name": "Nucor",           "color": "#8b5cf6"},
        {"ticker": "CTVA",  "name": "Corteva",         "color": "#ec4899"},
        {"ticker": "DD",    "name": "DuPont",          "color": "#06b6d4"},
        {"ticker": "PPG",   "name": "PPG Industries",  "color": "#84cc16"},
        {"ticker": "ALB",   "name": "Albemarle",       "color": "#f43f5e"},
        {"ticker": "MOS",   "name": "Mosaic",          "color": "#a78bfa"},
    ],
    "XLC": [
        {"ticker": "META",  "name": "Meta",            "color": "#00d4ff"},
        {"ticker": "GOOGL", "name": "Alphabet A",      "color": "#f59e0b"},
        {"ticker": "GOOG",  "name": "Alphabet C",      "color": "#10b981"},
        {"ticker": "NFLX",  "name": "Netflix",         "color": "#f97316"},
        {"ticker": "DIS",   "name": "Disney",          "color": "#8b5cf6"},
        {"ticker": "CHTR",  "name": "Charter",         "color": "#ec4899"},
        {"ticker": "TMUS",  "name": "T-Mobile",        "color": "#06b6d4"},
        {"ticker": "VZ",    "name": "Verizon",         "color": "#84cc16"},
        {"ticker": "T",     "name": "AT&T",            "color": "#f43f5e"},
        {"ticker": "EA",    "name": "EA",              "color": "#a78bfa"},
    ],
}


# ── Math helpers ─────────────────────────────────────────────────

def ema(values: List[float], period: int) -> List[float]:
    if not values:
        return []
    k = 2 / (period + 1)
    out = [values[0]]
    for i in range(1, len(values)):
        out.append(values[i] * k + out[i - 1] * (1 - k))
    return out


def pct_change(values: List[float], lookback: int = 1) -> List[float]:
    out: List[float] = []
    for i in range(len(values)):
        if i < lookback or values[i - lookback] == 0 or values[i - lookback] is None:
            out.append(0.0)
        else:
            out.append(((values[i] / values[i - lookback]) - 1) * 100)
    return out


def rolling_mean(values: List[float], end_idx: int, window: int) -> float:
    start = max(0, end_idx - window + 1)
    window_vals = [v for v in values[start:end_idx + 1] if math.isfinite(v)]
    return sum(window_vals) / len(window_vals) if window_vals else 0.0


def rolling_std(values: List[float], end_idx: int, window: int, mean: float) -> float:
    start = max(0, end_idx - window + 1)
    window_vals = [v for v in values[start:end_idx + 1] if math.isfinite(v)]
    if len(window_vals) < 2:
        return 1e-9
    sum_sq = sum((v - mean) ** 2 for v in window_vals)
    std = math.sqrt(sum_sq / len(window_vals))
    return std if std != 0 else 1e-9


def rolling_normalize_to_100(values: List[float], window: int = 26, scale: int = 8) -> List[float]:
    out: List[float] = []
    for i, v in enumerate(values):
        mean = rolling_mean(values, i, window)
        std = rolling_std(values, i, window, mean)
        z = (v - mean) / std
        out.append(100 + z * scale)
    return out


# ── Core RRG computation ─────────────────────────────────────────

def compute_rrg(
    raw_data: Dict[str, Dict[str, float]],
    benchmark: str = BENCHMARK,
    sectors: Optional[List[Dict[str, str]]] = None,
) -> List[Dict[str, Any]]:
    """
    Compute RRG coordinates for a list of sectors against a benchmark.

    Args:
        raw_data:  dict of ticker → {date_str → close_price}
        benchmark: benchmark ticker (default SPY for main chart,
                   sector ETF ticker for drill-down)
        sectors:   list of sector dicts with ticker/name/color
                   (default SECTORS for main chart,
                    SECTOR_HOLDINGS[x] for drill-down)
    """
    if sectors is None:
        sectors = SECTORS

    universe = [benchmark] + [s["ticker"] for s in sectors]
    date_sets = [set(raw_data.get(t, {}).keys()) for t in universe]
    common_dates = sorted(date_sets[0].intersection(*date_sets[1:]))

    if not common_dates:
        return []

    benchmark_prices = [raw_data[benchmark][d] for d in common_dates]

    results: List[Dict[str, Any]] = []

    for sec in sectors:
        sec_prices = [raw_data[sec["ticker"]][d] for d in common_dates]

        raw_rs: List[float] = []
        for i, p in enumerate(sec_prices):
            b = benchmark_prices[i]
            if not math.isfinite(p) or not math.isfinite(b) or b == 0:
                raw_rs.append(float("nan"))
            else:
                raw_rs.append(p / b)

        cleaned_raw_rs: List[float] = []
        for i, v in enumerate(raw_rs):
            if math.isfinite(v):
                cleaned_raw_rs.append(v)
                continue
            replacement = None
            for j in range(i - 1, -1, -1):
                if math.isfinite(raw_rs[j]):
                    replacement = raw_rs[j]
                    break
            if replacement is None:
                for j in range(i + 1, len(raw_rs)):
                    if math.isfinite(raw_rs[j]):
                        replacement = raw_rs[j]
                        break
            cleaned_raw_rs.append(replacement if replacement is not None else 1.0)

        rs_trend_raw = ema(cleaned_raw_rs, RS_EMA_PERIOD)
        rs_ratio = rolling_normalize_to_100(rs_trend_raw, NORM_WINDOW, ZSCORE_SCALE)

        rs_momentum_input = pct_change(rs_trend_raw, 1)
        rs_momentum_smoothed = ema(rs_momentum_input, MOM_EMA_PERIOD)
        rs_momentum = rolling_normalize_to_100(rs_momentum_smoothed, NORM_WINDOW, ZSCORE_SCALE)

        start = max(0, len(common_dates) - TAIL_LENGTH)
        trail = []
        for i in range(start, len(common_dates)):
            trail.append({
                "date": common_dates[i],
                "rs":   round(rs_ratio[i], 3),
                "mom":  round(rs_momentum[i], 3),
            })

        current = trail[-1]

        results.append({
            **sec,
            "rs":    current["rs"],
            "mom":   current["mom"],
            "trail": trail,
            "dates": common_dates,
        })

    return results
