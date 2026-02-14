import yfinance as yf
import pandas as pd
from .base import DataProvider
from datetime import datetime

class YahooFinanceProvider(DataProvider):
    """
    Data provider implementation using Yahoo Finance (yfinance).
    """
    
    def fetch_history(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetch historical data from Yahoo Finance.
        
        Args:
            symbol: Ticker symbol (e.g., 'AAPL').
            start: Start date (YYYY-MM-DD).
            end: End date (YYYY-MM-DD).
            
        Returns:
            pd.DataFrame: OHLCV data.
        """
        # Download data
        df = yf.download(symbol, start=start, end=end, progress=False, multi_level_index=False)
        
        if df.empty:
            raise ValueError(f"No data found for symbol {symbol} between {start} and {end}")
            
        # Ensure index is datetime and sorted
        df.index = pd.to_datetime(df.index)
        df.sort_index(inplace=True)
        
        return df

    def update_latest(self, symbol: str) -> pd.DataFrame:
        """
        Get the latest available data (convenience method).
        Fetches the last 5 days to ensure we get the most recent trading day.
        """
        end_date = datetime.now().strftime('%Y-%m-%d')
        # Simple approach: fetch last month to be safe, then take tail
        # For a production system we might want to be more specific
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d")
        return df
