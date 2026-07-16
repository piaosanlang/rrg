import akshare as ak
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
from rrg_math import compute_rrg, SECTOR_HOLDINGS

# ── Ticker universe ──────────────────────────────────────────────

SECTOR_TICKERS = [
    "SPY", "XLK", "XLF", "XLV", "XLE",
    "XLI", "XLY", "XLP", "XLU", "XLRE", "XLB", "XLC",

    # Macro snitches
    "HYG", "TLT", "GLD",

    # Additional ETFs
    "MAGS", "SOXX", "ARKK", "IWM", "IGV", "DRAM", "CIBR",
]

# Build full list of individual holding tickers (deduplicated)
HOLDING_TICKERS = list({
    h["ticker"]
    for holdings in SECTOR_HOLDINGS.values()
    for h in holdings
})

ALL_TICKERS = list(set(SECTOR_TICKERS + HOLDING_TICKERS))


# ── Data fetch ───────────────────────────────────────────────────

def fetch_weekly_from_daily() -> dict:
    """
    Download daily price data for all tickers from 2024-01-01
    and aggregate to weekly closes (last trading day of each week).

    Uses akshare for all tickers.

    Returns dict of ticker -> {date_str -> close_price}.
    """
    cache_dir = Path(".cache")
    cache_dir.mkdir(exist_ok=True)
    today = "2024-07-16"  # 固定日期避免系统时间影响

    data = {}
    total = len(ALL_TICKERS)

    for idx, ticker in enumerate(ALL_TICKERS, 1):
        source = "akshare"
        cache_file = cache_dir / f"{ticker}_{today}_ak.json"

        try:
            if cache_file.exists():
                with open(cache_file, "r") as f:
                    data[ticker] = json.load(f)
                print(f"  [{idx}/{total}] ✓ {ticker} ({source}, cached)")
                continue

            df = ak.stock_us_daily(symbol=ticker, adjust="")

            df = df.rename(columns={"date": "Date", "close": "Close"})
            df["Date"] = pd.to_datetime(df["Date"])
            df = df[df["Date"] >= "2024-01-01"]
            df = df.set_index("Date")

            df = df[["Close"]].dropna().copy()
            df["week"] = df.index.to_period("W-FRI")

            weekly_data = {}
            for _, group in df.groupby("week"):
                last_trading_day = group.index.max()
                last_close = group["Close"].iloc[-1]
                weekly_data[
                    last_trading_day.strftime("%Y-%m-%d")
                ] = round(float(last_close), 2)

            data[ticker] = weekly_data

            # Save to cache
            with open(cache_file, "w") as f:
                json.dump(weekly_data, f, indent=2)

            print(f"  [{idx}/{total}] ✓ {ticker} ({source})")

        except Exception as e:
            print(f"  [{idx}/{total}] ✗ {ticker} ({source}) — {e}")

    return data


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 50)
    print("Fetching price data...")
    print("=" * 50)
    raw_data = fetch_weekly_from_daily()

    public_dir = Path("public")
    public_dir.mkdir(exist_ok=True)

    # ── Main sector RRG ──────────────────────────────
    print("\nComputing main sector RRG...")
    rrg_data = compute_rrg(raw_data)

    with open(public_dir / "raw-data.json", "w") as f:
        json.dump(raw_data, f, indent=2)
    print("  ✓ public/raw-data.json")

    with open(public_dir / "rrg-data.json", "w") as f:
        json.dump(rrg_data, f, indent=2)
    print("  ✓ public/rrg-data.json")

    # ── Drill-down RRGs ──────────────────────────────
    print("\nComputing drill-down RRGs...")
    success = 0
    failed = 0

    for sector_ticker, holdings in SECTOR_HOLDINGS.items():
        try:
            drilldown_data = compute_rrg(
                raw_data,
                benchmark=sector_ticker,
                sectors=holdings,
            )

            filename = public_dir / f"rrg-{sector_ticker.lower()}.json"
            with open(filename, "w") as f:
                json.dump(drilldown_data, f, indent=2)

            print(f"  ✓ {filename}")
            success += 1

        except Exception as e:
            print(f"  ✗ {sector_ticker} drill-down failed — {e}")
            failed += 1

    # ── Summary ──────────────────────────────────────
    print("\n" + "=" * 50)
    print(f"Done.")
    print(f"  Main RRG:       ✓")
    print(f"  Drill-downs:    {success} succeeded, {failed} failed")
    print(f"  Total tickers:  {len(ALL_TICKERS)}")
    print("=" * 50)


if __name__ == "__main__":
    main()
