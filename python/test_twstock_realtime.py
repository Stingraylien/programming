import twstock

try:
    print("Fetching realtime data...")
    real = twstock.realtime.get('2330')
    print(f"Realtime: {real}")
    if real['success']:
        print(f"Name: {real['info']['name']}")
        print(f"Latest Price: {real['realtime']['latest_trade_price']}")
except Exception as e:
    print(f"twstock realtime error: {e}")
