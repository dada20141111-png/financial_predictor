from abc import ABC, abstractmethod
import pandas as pd
from typing import Any, Dict, List, Optional

class DataProvider(ABC):
    """Abstract base class for data providers."""
    
    @abstractmethod
    def fetch_history(self, symbol: str, start: str, end: str) -> pd.DataFrame:
        """
        Fetch historical data for a given symbol.
        
        Args:
            symbol: The asset symbol (e.g., 'AAPL', 'BTC-USD').
            start: Start date strings (YYYY-MM-DD).
            end: End date strings (YYYY-MM-DD).
            
        Returns:
            pd.DataFrame: Historical data with Date index.
        """
        pass

class FeatureTransformer(ABC):
    """Abstract base class for feature transformers."""
    
    @abstractmethod
    def transform(self, input_data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply transformation to input data.
        
        Args:
            input_data: Raw data DataFrame.
            
        Returns:
            pd.DataFrame: Transformed data with new features.
        """
        pass

class Predictor(ABC):
    """Abstract base class for prediction models."""
    
    @abstractmethod
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train the model.
        
        Args:
            X: Features DataFrame.
            y: Target Series.
        """
        pass
        
    @abstractmethod
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions.
        
        Args:
            X: Features DataFrame.
            
        Returns:
            pd.Series: Predicted values.
        """
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """Save the model to disk."""
        pass
        
    @abstractmethod
    def load(self, path: str) -> None:
        """Load the model from disk."""
        pass

class Evaluator(ABC):
    """Abstract base class for model evaluation."""
    
    @abstractmethod
    def evaluate(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
        """
        Calculate evaluation metrics.
        
        Args:
            y_true: True target values.
            y_pred: Predicted values.
            
        Returns:
            Dict: Dictionary of metric names and values.
        """
        pass
