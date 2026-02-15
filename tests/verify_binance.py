import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from exchange import ExchangeProvider
from execution import BinanceExecutor

def test_data_fetching():
    print("--- Testing Data Fetching (Public API) ---")
    try:
        provider = ExchangeProvider(exchange_id='binance')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        symbol = 'BTC/USDT'
        print(f"Fetching {symbol} from {start_date} to {end_date}...")
        
        df = provider.fetch_history(symbol, start=start_date, end=end_date)
        
        if not df.empty:
            print(f"Success! Fetched {len(df)} rows.")
            print(df.head(2))
            print(df.tail(2))
        else:
            print("Failed: DataFrame is empty.")
            
    except Exception as e:
        print(f"Error: {e}")

def test_mock_execution():
    print("\n--- Testing Mock Execution (Dry Run) ---")
    try:
        # Dry Run = True means no API keys needed for safety
        executor = BinanceExecutor(dry_run=True)
        
        # Check Balance
        usdt_bal = executor.get_balance('USDT')
        print(f"Simulated USDT Balance: {usdt_bal}")
        
        # Place Buy Order
        print("Placing BUY order for 0.1 BTC...")
        order_buy = executor.place_order('BTC/USDT', 'buy', 0.1, price=50000.0)
        print("Order Result:", order_buy)
        
        # Check Balance Again
        btc_bal = executor.get_balance('BTC')
        print(f"Simulated BTC Balance: {btc_bal}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_data_fetching()
    test_mock_execution()
