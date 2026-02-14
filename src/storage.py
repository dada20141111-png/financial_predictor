import pandas as pd
import os
from typing import Optional

class StorageManager:
    """
    Manages local storage of financial data using Parquet format.
    """
    
    def __init__(self, data_dir: str):
        """
        Args:
            data_dir: Directory to store data files.
        """
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
    def _get_file_path(self, symbol: str) -> str:
        # Sanitize symbol for filename (e.g., ^GSPC -> GSPC)
        safe_symbol = symbol.replace('^', '').replace('=', '')
        return os.path.join(self.data_dir, f"{safe_symbol}.parquet")
    
    def save_data(self, symbol: str, data: pd.DataFrame) -> None:
        """
        Save dataframe to parquet.
        """
        file_path = self._get_file_path(symbol)
        data.to_parquet(file_path)
        
    def load_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        Load dataframe from parquet. Returns None if not found.
        """
        file_path = self._get_file_path(symbol)
        if not os.path.exists(file_path):
            return None
        return pd.read_parquet(file_path)
        
    def exists(self, symbol: str) -> bool:
        return os.path.exists(self._get_file_path(symbol))
