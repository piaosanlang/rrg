import yfinance as yf
import json
import pandas as pd
from pathlib import Path

tickers = ["SPY", "XLK", "XLF", "XLV", "XLE",
           "XLI", "XLY", "XLP", "XLU", "XLRE", "XLB", "XLC"]

data = {}

for ticker in tickers:
    df = yf.download(
        ticker,
        period="2y",
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    # Flatten multi-level columns if present
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    # Keep only close and drop missing values
    df = df[["Close"]].dropna().copy()

    # Ensure datetime index
    df.index = pd.to_datetime(df.index)

    # Group by week ending Friday
    df["week"] = df.index.to_period("W-FRI")

    weekly_data = {}

    for _, group in df.groupby("week"):
        last_trading_day = group.index.max()
        last_close = group["Close"].iloc[-1]

        weekly_data[last_trading_day.strftime("%Y-%m-%d")] = round(float(last_close), 2)

    data[ticker] = weekly_data

# 👇 IMPORTANT: write to your React public folder
output_path = Path("public/raw-data.json")

with open(output_path, "w") as f:
    json.dump(data, f, indent=2)

print("raw-data.json updated")
