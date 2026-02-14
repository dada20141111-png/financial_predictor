import pandas as pd
import numpy as np
from typing import List, Optional
import seaborn as sns
import matplotlib.pyplot as plt

class CorrelationTransformer:
    """
    Computes rolling correlations between assets.
    """
    
    def transform(self, df: pd.DataFrame, target_col: str, window: int = 30) -> pd.DataFrame:
        """
        Appends rolling correlation columns to the dataframe.
        Args:
            df: DataFrame containing multiple asset prices.
            target_col: The primary asset column name (e.g., 'Close').
            window: Rolling window size.
            
        Returns:
            DataFrame with new correlation columns.
        """
        df_out = df.copy()
        
        # Assume other columns are potential correlates
        # We need to distinguish feature columns from raw asset columns.
        # In this architecture, we likely merged macro data resulting in columns like 'Gold', 'Oil'.
        
        # Iterate over columns that are NOT the target
        for col in df.columns:
            if col == target_col:
                continue
            
            # Skip if column is not numeric
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
                
            col_name = f"Corr_{col}_{window}"
            df_out[col_name] = df[target_col].rolling(window=window).corr(df[col])
            
        return df_out

class MarketAnalyzer:
    """
    Performs static analysis on market data.
    """
    
    def calculate_correlation_matrix(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Returns the correlation matrix of the dataframe.
        """
        return df.corr()
    
    def plot_correlation_heatmap(self, df: pd.DataFrame, title: str = "Correlation Matrix"):
        """
        Plots a heatmap of correlations.
        
        Note: In a headless environment this might default to non-interactive backend.
        """
        corr = df.corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title(title)
        return plt
        
    def analyze_lag_correlation(self, target: pd.Series, feature: pd.Series, max_lag: int = 10) -> pd.Series:
        """
        Analyzes correlation at different lags to find leading indicators.
        
        Args:
            target: The target series (e.g., BTC return).
            feature: The feature series (e.g., VIX).
            max_lag: Maximum days to shift feature forward.
            
        Returns:
            Series with index=lag and value=correlation.
        """
        corrs = {}
        for lag in range(1, max_lag + 1):
            # Shift feature forward (feature happens *before* target)
            # If feature at T correlates with target at T+k, then feature is a leading indicator.
            # Shift(1) moves T to T+1. 
            shifted_feature = feature.shift(lag)
            corr = target.corr(shifted_feature)
            corrs[lag] = corr
            
        return pd.Series(corrs, name="Lag_Correlation")
