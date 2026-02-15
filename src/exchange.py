import ccxt
import pandas as pd
from datetime import datetime
import time
from typing import Optional
if __package__:
    from .base import DataProvider
else:
    # Fallback for running script directly or with weird pathing
    import sys
    import os
    sys.path.append(os.path.dirname(__file__))
    from base import DataProvider


class ExchangeProvider(DataProvider):
    """
    Data provider implementation using ccxt for crypto exchanges.
    Supports Binance and OKX.
    """
    
    def __init__(self, exchange_id: str = 'binance', api_key: str = None, secret: str = None):
        """
        Initialize the exchange provider.
        
        Args:
            exchange_id: 'binance' or 'okx'.
            api_key: Optional API key (not needed for public data).
            secret: Optional Secret key.
        """
        self.exchange_id = exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        
        config = {
            'enableRateLimit': True,  # ccxt handles rate limits automatically
        }
        
        if api_key and secret:
            config['apiKey'] = api_key
            config['secret'] = secret
            
        self.exchange = exchange_class(config)
        self.exchange.load_markets()

    def fetch_history(self, symbol: str, start: str, end: str, timeframe: str = '1d') -> pd.DataFrame:
        """
        Fetch historical OHLCV data.
        
        Args:
            symbol: Unified symbol (e.g., 'BTC/USDT').
            start: Start date (YYYY-MM-DD).
            end: End date (YYYY-MM-DD).
            timeframe: '1d', '1h', '15m', etc.
            
        Returns:
            pd.DataFrame: OHLCV data.
        """
        if not self.exchange.has['fetchOHLCV']:
            raise NotImplementedError(f"{self.exchange_id} does not support fetchOHLCV")

        # Convert start/end to milliseconds timestamp
        # ccxt parse8601 expects ISO8601 string
        start_ts = self.exchange.parse8601(f"{start}T00:00:00Z")
        end_ts = self.exchange.parse8601(f"{end}T23:59:59Z")
        
        all_ohlcv = []
        since = start_ts
        
        # Limit per request (Exchange dependent, 1000 is safe for Binance)
        limit = 1000
        
        # Pagination loop
        while since < end_ts:
            try:
                # Fetch data
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since, limit=limit)
                
                if not ohlcv:
                    break
                    
                # Append to list
                all_ohlcv.extend(ohlcv)
                
                # Update 'since'
                last_ts = ohlcv[-1][0]
                
                # Careful with infinite loops if exchange returns same data or 'since' doesn't advance
                # Calculate expected duration of one candle in ms
                duration_seconds = self.exchange.parse_timeframe(timeframe)
                duration_ms = duration_seconds * 1000
                
                # Ideally, next fetch starts at last_ts + duration
                # But to be safe and avoid gaps, sometimes start at last_ts + 1ms is used
                # However, consistent with ccxt best practice:
                since = last_ts + 1
                
                # Break if we reached end
                if last_ts >= end_ts:
                    break
                    
                # Rate limit sleep is handled by ccxt enableRateLimit=True in init
                
            except Exception as e:
                print(f"Error fetching data from {self.exchange_id}: {e}")
                time.sleep(1)
                break
        
        if not all_ohlcv:
            return pd.DataFrame()
            
        # Convert to DataFrame
        # CCXT format: [timestamp, open, high, low, close, volume]
        df = pd.DataFrame(all_ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms')
        df.set_index('Date', inplace=True)
        df.drop(columns=['Timestamp'], inplace=True)
        
        # Filter by requested range (fetch might overshoot)
        # Using string comparison for index filtering
        df = df[(df.index >= pd.Timestamp(start)) & (df.index <= pd.Timestamp(end) + pd.Timedelta(days=1))]
        
        # Deduplicate just in case
        df = df[~df.index.duplicated(keep='first')]
        
        return df
