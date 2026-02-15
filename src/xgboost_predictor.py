import pandas as pd
import numpy as np
import pickle
import xgboost as xgb
from typing import Dict, Any
from .base import Predictor

class XGBoostPredictor(Predictor):
    """
    Predictor implementation using XGBoost.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize with XGBoost parameters.
        """
        self.params = {
            'objective': 'reg:squarederror',
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 5,
            'eval_metric': 'rmse'
        }
        
        # Override defaults with provided kwargs
        if kwargs:
            self.params.update(kwargs)
            
        self.model = xgb.XGBRegressor(**self.params)
        
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train the XGBoost model.
        """
        self.model.fit(X, y)
        
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions.
        """
        predictions = self.model.predict(X)
        return pd.Series(predictions, index=X.index)
        
    def save(self, path: str) -> None:
        """
        Save model to file.
        """
        self.model.save_model(path)
        
    def load(self, path: str) -> None:
        """
        Load model from file.
        """
        self.model = xgb.XGBRegressor()
        self.model.load_model(path)
        
    def get_feature_importance(self) -> pd.Series:
        """
        Returns feature importance as a Series.
        """
        return pd.Series(
            self.model.feature_importances_, 
            index=self.model.feature_names_in_
        ).sort_values(ascending=False)

    def tune_hyperparameters(self, X: pd.DataFrame, y: pd.Series, n_trials: int = 20) -> Dict[str, Any]:
        """
        Tune hyperparameters using Optuna and update the model.
        """
        from .optimizer import Optimizer
        optimizer = Optimizer(n_trials=n_trials)
        best_params = optimizer.optimize_xgboost(X, y)
        
        # Merge best params with base functional params
        # (objective and eval_metric are sometimes not returned by search if fixed in obj function, 
        # but in our Optimizer we return study.best_trial.params which only has suggested ones)
        
        # We need to ensure required base params are present
        final_params = {
            'objective': 'reg:squarederror',
            'eval_metric': 'rmse'
        }
        final_params.update(best_params)
        
        self.params = final_params
        # Re-initialize model with new params
        self.model = xgb.XGBRegressor(**self.params)
        
        return self.params
