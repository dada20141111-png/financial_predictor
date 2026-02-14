import pandas as pd
from .base import FeatureTransformer

class TechnicalIndicatorTransformer(FeatureTransformer):
    """
    Calculates technical indicators such as MA, RSI, MACD.
    """
    
    def transform(self, input_data: pd.DataFrame) -> pd.DataFrame:
        """
        Adds technical indicators to the input dataframe.
        Expects input_data to have 'Close' column.
        """
        df = input_data.copy()
        
        # Simple Moving Averages
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        # Exponential Moving Average
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # Fill NaNs (or leave them to handle later? For now, we leave them)
        return df

class MacroFeatureTransformer(FeatureTransformer):
    """
    Handles macro-economic data alignment and feature creation.
    """
    def transform(self, input_data: pd.DataFrame) -> pd.DataFrame:
        # Placeholder for macro integration
        return input_data
