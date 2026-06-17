import json
import os
import yfinance as yf
import pandas as pd
from datetime import datetime

PORTFOLIO_FILE = os.path.join(os.path.dirname(__file__), 'data/portfolio.json')

# --- Data Persistence ---
def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    try:
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_portfolio(portfolio_data):
    os.makedirs(os.path.dirname(PORTFOLIO_FILE), exist_ok=True)
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio_data, f, indent=4)

def add_transaction(ticker, amount, price, currency):
    """
    Update the portfolio with a new transaction.
    """
    # Normalize ticker: US stocks often entered as TSM.US, convert to TSM
    # BUT keep .TW as is.
    if ticker.endswith(".US"):
        ticker = ticker.replace(".US", "")
        
    portfolio = load_portfolio()
    # Check if stock exists
    existing_stock = next((item for item in portfolio if item['ticker'] == ticker), None)
    
    if existing_stock:
        # Calculate new weighted average cost
        total_quantity = existing_stock['quantity'] + amount
        if total_quantity <= 0:
            # If selling all or more, remove or handle logic
            # For simplicity in this MVP, we remove if quantity <= 0
            portfolio = [item for item in portfolio if item['ticker'] != ticker]
        else:
            # Update weighted average cost
            current_total_cost = existing_stock['quantity'] * existing_stock['avg_cost']
            new_tx_cost = amount * price
            new_avg_cost = (current_total_cost + new_tx_cost) / total_quantity
            
            existing_stock['quantity'] = total_quantity
            existing_stock['avg_cost'] = new_avg_cost
    else:
        if amount > 0:
            portfolio.append({
                'ticker': ticker,
                'quantity': amount,
                'avg_cost': price,
                'currency': currency
            })
    
    save_portfolio(portfolio)

# --- Market Data ---
# --- Market Data ---
def get_market_data(portfolio):
    """
    Fetches real-time data using Hybrid Strategy:
    - TW Stocks: twstock (Realtime API)
    - US Stocks: yfinance
    - FX Rate: yfinance
    """
    import requests
    import twstock
    
    # Create a custom session for yfinance to avoid basic rate limiting
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })

    tw_tickers = []
    us_tickers = []
    names = {} # Store stock names: {ticker: name}
    success_flag = True # Optimistic start
    
    # 1. Classify Tickers
    for item in portfolio:
        t = item['ticker']
        if t.endswith('.TW'):
             tw_tickers.append(t.replace('.TW', ''))
        elif t.isdigit(): 
             tw_tickers.append(t)
        else:
             if t.endswith('.US'):
                 us_tickers.append(t.replace('.US', ''))
             else:
                 us_tickers.append(t)
                 
    # Deduplicate
    tw_tickers = list(set(tw_tickers))
    us_tickers = list(set(us_tickers))
    
    market_data = {}

    # 2. Fetch TW Data (twstock)
    if tw_tickers:
        try:
            real_data = twstock.realtime.get(tw_tickers)
            
            # Helper to parse one result
            def parse_tw_result(symbol, result):
                if result.get('success'):
                    # Name
                    name = result.get('info', {}).get('name', symbol)
                    try:
                        price = float(result['realtime']['latest_trade_price'])
                        return price, name
                    except:
                        return 0.0, name
                return 0.0, symbol

            if isinstance(real_data, dict):
                for symbol, res in real_data.items():
                    if symbol == 'success':
                        continue
                    price, name = parse_tw_result(symbol, res)
                    
                    if price > 0:
                        market_data[symbol] = price
                        market_data[symbol + '.TW'] = price
                        
                    names[symbol] = name
                    names[symbol + '.TW'] = name

        except Exception as e:
            print(f"twstock Error: {e}")
            success_flag = False

    # 3. Fetch US Data (yfinance)
    if us_tickers:
        for ticker in us_tickers:
            try:
                t = yf.Ticker(ticker, session=session)
                hist = t.history(period="1d")
                if not hist.empty:
                    market_data[ticker] = hist['Close'].iloc[-1]
                    try:
                         short_name = t.info.get('shortName', ticker)
                         names[ticker] = short_name
                    except:
                         names[ticker] = ticker
                else:
                    market_data[ticker] = t.info.get('previousClose', 0.0)
                    names[ticker] = ticker
            except Exception as e:
                print(f"US Stock Error {ticker}: {e}")
                market_data[ticker] = 0.0
                names[ticker] = ticker
                
    # 4. Fetch FX (yfinance)
    fx_rate = 30.0
    try:
        t_fx = yf.Ticker("TWD=X", session=session)
        hist = t_fx.history(period="1d")
        if not hist.empty:
            fx_rate = hist['Close'].iloc[-1]
    except Exception as e:
        print(f"FX Error: {e}")
        
    return market_data, fx_rate, names, success_flag

def calculate_portfolio_value(portfolio, market_data, fx_rate, names={}):
    """
    Enhances the portfolio list with current value, P/L, etc.
    """
    total_value_twd = 0.0
    total_cost_twd = 0.0
    
    enriched_portfolio = []
    
    for item in portfolio:
        original_ticker = item['ticker']
        # Clean ticker to match market_data keys
        ticker = original_ticker
        if ticker.endswith(".US"):
            ticker = ticker.replace(".US", "")
            
        qty = item['quantity']
        avg_cost = item['avg_cost']
        currency = item['currency']
        
        current_price = market_data.get(ticker, 0.0)
        stock_name = names.get(ticker, original_ticker)
        
        if current_price == 0.0:
            # Fallback to cost if no price found to avoid -100% P/L shock?
            # Or keep 0 to indicate error?
            # Let's keep 0 but logic in UI should handle it.
            pass
        
        # Calculate Value in Original Currency
        market_value_native = current_price * qty
        cost_basis_native = avg_cost * qty
        pl_native = market_value_native - cost_basis_native
        
        # Convert to TWD
        if currency == 'USD':
            market_value_twd = market_value_native * fx_rate
            cost_basis_twd = cost_basis_native * fx_rate 
        else:
            market_value_twd = market_value_native
            cost_basis_twd = cost_basis_native
            
        pl_twd = market_value_twd - cost_basis_twd
        pl_percent = (pl_twd / cost_basis_twd * 100) if cost_basis_twd != 0 else 0
        
        total_value_twd += market_value_twd
        total_cost_twd += cost_basis_twd
        
        enriched_portfolio.append({
            **item,
            'ticker': ticker, 
            'name': stock_name,
            'current_price': current_price,
            'market_value_native': market_value_native,
            'market_value_twd': market_value_twd,
            'pl_twd': pl_twd,
            'pl_percent': pl_percent
        })
        
    return enriched_portfolio, total_value_twd, total_cost_twd
