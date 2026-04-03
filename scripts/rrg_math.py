from typing import Dict, List, Any
import math


BENCHMARK = "SPY"

RS_EMA_PERIOD = 10
MOM_EMA_PERIOD = 5
NORM_WINDOW = 39
TAIL_LENGTH = 12
ZSCORE_SCALE = 6

SECTORS = [
    {"ticker": "XLK", "name": "Technology",     "color": "#00d4ff"},
    {"ticker": "XLF", "name": "Financials",     "color": "#f59e0b"},
    {"ticker": "XLV", "name": "Health Care",    "color": "#10b981"},
    {"ticker": "XLE", "name": "Energy",         "color": "#f97316"},
    {"ticker": "XLI", "name": "Industrials",    "color": "#8b5cf6"},
    {"ticker": "XLY", "name": "Cons. Discret.", "color": "#ec4899"},
    {"ticker": "XLP", "name": "Cons. Staples",  "color": "#06b6d4"},
    {"ticker": "XLU", "name": "Utilities",      "color": "#84cc16"},
    {"ticker": "XLRE", "name": "Real Estate",   "color": "#f43f5e"},
    {"ticker": "XLB", "name": "Materials",      "color": "#a78bfa"},
    {"ticker": "XLC", "name": "Comm. Services", "color": "#fb923c"},
]


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


def compute_rrg(raw_data: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
    universe = [BENCHMARK] + [s["ticker"] for s in SECTORS]
    date_sets = [set(raw_data.get(t, {}).keys()) for t in universe]
    common_dates = sorted(date_sets[0].intersection(*date_sets[1:]))

    benchmark_prices = [raw_data[BENCHMARK][d] for d in common_dates]

    results: List[Dict[str, Any]] = []

    for sec in SECTORS:
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
                "rs": round(rs_ratio[i], 3),
                "mom": round(rs_momentum[i], 3),
            })

        current = trail[-1]

        results.append({
            **sec,
            "rs": current["rs"],
            "mom": current["mom"],
            "trail": trail,
            "dates": common_dates,
        })

    return results
