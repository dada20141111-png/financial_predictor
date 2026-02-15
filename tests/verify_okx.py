import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from exchange import ExchangeProvider
from execution import OKXExecutor

def test_data_fetching():
    print("--- Testing OKX Data Fetching (Public API) ---")
    try:
        # Use OKX
        provider = ExchangeProvider(exchange_id='okx')
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        
        symbol = 'BTC/USDT'
        print(f"Fetching {symbol} from {start_date} to {end_date}...")
        
        df = provider.fetch_history(symbol, start=start_date, end=end_date, timeframe='1h')
        
        if not df.empty:
            print(f"Success! Fetched {len(df)} rows.")
            print(df.head(2))
            print(df.tail(2))
        else:
            print("Failed: DataFrame is empty.")
            
    except Exception as e:
        print(f"Error: {e}")

def test_paper_trading_persistence():
    print("\n--- Testing OKX Paper Trading Persistence ---")
    try:
        # 1. Init Executor
        print("Initializing Executor...")
        executor = OKXExecutor(mode='paper', paper_balance_file='test_balance.json')
        
        # Reset balance for test
        executor.simulated_balance = {'USDT': 10000.0, 'BTC': 0.0}
        executor._save_paper_balance()
        
        initial_usdt = executor.get_balance('USDT')
        print(f"Initial USDT: {initial_usdt}")
        
        # 2. Place Buy Order
        print("Placing Buy Order (0.1 BTC @ 50000)...")
        executor.place_order('BTC/USDT', 'buy', 0.1, price=50000.0)
        
        after_trade_usdt = executor.get_balance('USDT')
        print(f"USDT after trade: {after_trade_usdt}")
        
        assert after_trade_usdt == 5000.0
        
        # 3. Re-init verify persistence
        print("Re-initializing Executor (Simulating Restart)...")
        executor_new = OKXExecutor(mode='paper', paper_balance_file='test_balance.json')
        
        reloaded_usdt = executor_new.get_balance('USDT')
        print(f"Reloaded USDT: {reloaded_usdt}")
        
        if reloaded_usdt == 5000.0:
            print("SUCCESS: Balance persisted correctly.")
        else:
            print(f"FAILURE: Expected 5000.0, got {reloaded_usdt}")
            
        # Cleanup
        if os.path.exists('test_balance.json'):
            os.remove('test_balance.json')
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_data_fetching()
    test_paper_trading_persistence()
