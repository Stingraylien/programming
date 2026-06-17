import yfinance as yf
print("Imported yfinance successfully")
try:
    fx = yf.Ticker("TWD=X")
    print(f"Created Ticker object: {fx}")
    hist = fx.history(period="1d")
    print("Fetched history")
    print(hist.head())
except Exception as e:
    import traceback
    traceback.print_exc()
