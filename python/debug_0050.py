import twstock
print("Fetching 0050...")
try:
    real = twstock.realtime.get('0050')
    print(real)
except Exception as e:
    print(e)
