import utils
import json

# Create a mock portfolio matching user's data
portfolio = [
    {
        "ticker": "0050.TW",
        "quantity": 38.0,
        "avg_cost": 62.21,
        "currency": "TWD"
    },
    {
        "ticker": "TSM.US",
        "quantity": 2.0,
        "avg_cost": 188.98,
        "currency": "USD"
    }
]

print("Testing utils.get_market_data with portfolio...")
data, fx, names, success = utils.get_market_data(portfolio)
print(f"FX Rate: {fx}")
print(f"Market Data: {data}")
print(f"Names: {names}")
print(f"Success Flag: {success}")

if not data:
    print("Failed to fetch data.")
else:
    print("Success!")
