import yfinance as yf
import json
import pandas as pd
from pathlib import Path

from scripts.rrg_math import compute_rrg

TICKERS = [
    "SPY", "XLK", "XLF", "XLV", "XLE",
    "XLI", "XLY", "XLP", "XLU", "XLRE", "XLB", "XLC"
]


def fetch_weekly_from_daily():
    data = {}

    for ticker in TICKERS:
        df = yf.download(
            ticker,
            period="2y",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df = df[["Close"]].dropna().copy()
        df.index = pd.to_datetime(df.index)

        df["week"] = df.index.to_period("W-FRI")

        weekly_data = {}

        for _, group in df.groupby("week"):
            last_trading_day = group.index.max()
            last_close = group["Close"].iloc[-1]
            weekly_data[last_trading_day.strftime("%Y-%m-%d")] = round(float(last_close), 2)

        data[ticker] = weekly_data

    return data


def main():
    raw_data = fetch_weekly_from_daily()
    rrg_data = compute_rrg(raw_data)

    public_dir = Path("public")
    raw_output = public_dir / "raw-data.json"
    rrg_output = public_dir / "rrg-data.json"

    with open(raw_output, "w") as f:
        json.dump(raw_data, f, indent=2)

    with open(rrg_output, "w") as f:
        json.dump(rrg_data, f, indent=2)

    print("Updated public/raw-data.json")
    print("Updated public/rrg-data.json")


if __name__ == "__main__":
    main()
