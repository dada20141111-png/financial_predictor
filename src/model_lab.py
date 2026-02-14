import pandas as pd
import numpy as np
import pickle
from typing import Dict, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from .base import Predictor, Evaluator

class LinearRegressionPredictor(Predictor):
    """
    Baseline predictor using Linear Regression.
    """
    
    def __init__(self):
        self.model = LinearRegression()
        
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train the linear regression model.
        """
        self.model.fit(X, y)
        
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions.
        """
        predictions = self.model.predict(X)
        return pd.Series(predictions, index=X.index)
    
    def save(self, path: str) -> None:
        """Save model using pickle."""
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
            
    def load(self, path: str) -> None:
        """Load model using pickle."""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)

class SimpleEvaluator(Evaluator):
    """
    Calculates MSE and R2 score.
    """
    
    def evaluate(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        return {"MSE": mse, "R2": r2}

class TimeSeriesSplitter:
    """
    Custom splitter for time series data to avoid look-ahead bias.
    """
    def __init__(self, n_splits: int = 5):
        self.n_splits = n_splits
        
    def split(self, X: pd.DataFrame) -> list[Tuple[pd.Index, pd.Index]]:
        """
        Returns list of (train_idx, test_idx)
        """
        from sklearn.model_selection import TimeSeriesSplit
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        return list(tscv.split(X))
