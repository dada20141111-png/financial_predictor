import pandas as pd
from typing import List, Dict

class DataMerger:
    """
    Aligns and merges multiple time series DataFrames.
    """
    
    def merge(self, 
              target_data: pd.DataFrame, 
              macro_data_dict: Dict[str, pd.DataFrame], 
              method: str = 'ffill') -> pd.DataFrame:
        """
        Merges macro data into the target asset's DataFrame.
        
        Args:
            target_data: The main asset DataFrame (e.g., BTC). Index must be DatetimeIndex.
            macro_data_dict: Dictionary mapping names (e.g., 'Gold') to DataFrames.
            method: 'ffill' (forward fill) recommended to avoid look-ahead bias.
            
        Returns:
            pd.DataFrame: Merged DataFrame with macro columns prefixed.
        """
        merged_df = target_data.copy()
        
        for name, df in macro_data_dict.items():
            # Ensure we only use 'Close' price for macro indicators usually
            # If df has 'Close', use it. Otherwise assume it's a Series or single-col DF
            if isinstance(df, pd.DataFrame) and 'Close' in df.columns:
                series = df['Close']
            elif isinstance(df, pd.DataFrame) and len(df.columns) == 1:
                series = df.iloc[:, 0]
            elif isinstance(df, pd.Series):
                series = df
            else:
                raise ValueError(f"Cannot extract data from {name}")
                
            # Rename series
            series.name = name
            
            # Merge logic: Left join on target index
            # This ensures we only keep rows where the target asset traded.
            merged_df = merged_df.join(series, how='left')
            
            # Forward fill missing values (e.g., macro data missing on weekends/holidays)
            if method == 'ffill':
                merged_df[name] = merged_df[name].ffill()
                
        return merged_df
