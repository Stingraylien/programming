import yfinance as yf
import pandas as pd

tickers = ["0050.TW", "TSM.US", "TSM", "TWD=X"]
print(f"Testing tickers: {tickers}")

for t in tickers:
    print(f"\n--- Fetching {t} ---")
    try:
        ticker_obj = yf.Ticker(t)
        hist = ticker_obj.history(period="1d")
        if hist.empty:
            print(f"No history found for {t}")
            # Try getting info just in case
            try:
                info = ticker_obj.info
                print(f"Info found, current price maybe: {info.get('currentPrice') or info.get('regularMarketPrice')}")
            except:
                print("No info found either")
        else:
            print(f"Success! Last close: {hist['Close'].iloc[-1]}")
    except Exception as e:
        print(f"Error fetching {t}: {e}")
