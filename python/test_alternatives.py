import twstock
import pandas as pd
from FinMind.data import DataLoader

print("--- Testing twstock (TW Only) ---")
try:
    stock = twstock.Stock('2330')
    print(f"2330 Capacity: {stock.capacity}")
    print(f"2330 Price: {stock.price[-1] if stock.price else 'N/A'}")
    
    real = twstock.realtime.get('2330')
    print(f"Realtime: {real}")
except Exception as e:
    print(f"twstock error: {e}")

print("\n--- Testing FinMind (TW Only) ---")
try:
    dl = DataLoader()
    # FinMind usually fetches historical data well
    data = dl.taiwan_stock_daily(stock_id='2330', start_date='2023-12-01')
    if not data.empty:
        print(f"FinMind 2330 Last Close: {data.iloc[-1]['close']}")
    else:
        print("FinMind returned empty data")
except Exception as e:
    print(f"FinMind error: {e}")
