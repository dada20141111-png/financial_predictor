
import pandas as pd
import numpy as np
import pickle
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, Tuple
import os

from .base import Predictor

class MLPPredictor(Predictor):
    """
    Predictor implementation using Scikit-learn MLPRegressor (Neural Network).
    """
    
    def __init__(self, hidden_layer_sizes: Tuple[int, ...] = (100, 50), 
                 activation: str = 'relu', solver: str = 'adam', 
                 max_iter: int = 500, random_state: int = 42):
        
        self.hidden_layer_sizes = hidden_layer_sizes
        self.activation = activation
        self.solver = solver
        self.max_iter = max_iter
        self.random_state = random_state
        
        # Neural Networks result require scaling
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
        self.model = MLPRegressor(
            hidden_layer_sizes=self.hidden_layer_sizes,
            activation=self.activation,
            solver=self.solver,
            max_iter=self.max_iter,
            random_state=self.random_state,
            early_stopping=True, # Prevent overfitting
            validation_fraction=0.1
        )
        
        self.is_fitted = False
        
    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Train the MLP model. Autoscales data.
        """
        # Fit scalers
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.values.reshape(-1, 1))
        
        # Train
        self.model.fit(X_scaled, y_scaled.ravel())
        self.is_fitted = True
        
    def predict(self, X: pd.DataFrame) -> pd.Series:
        """
        Make predictions. Autoscales input and inverse scales output.
        """
        if not self.is_fitted:
            raise RuntimeError("Model is not trained yet.")
            
        X_scaled = self.scaler_X.transform(X)
        preds_scaled = self.model.predict(X_scaled)
        
        # Inverse transform to get actual price/value
        preds = self.scaler_y.inverse_transform(preds_scaled.reshape(-1, 1))
        
        return pd.Series(preds.flatten(), index=X.index)
        
    def save(self, path: str) -> None:
        """
        Save model and scalers using pickle.
        """
        data = {
            'model': self.model,
            'scaler_X': self.scaler_X,
            'scaler_y': self.scaler_y,
            'is_fitted': self.is_fitted
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
            
    def load(self, path: str) -> None:
        """
        Load model and scalers.
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)
            
        self.model = data['model']
        self.scaler_X = data['scaler_X']
        self.scaler_y = data['scaler_y']
        self.is_fitted = data['is_fitted']
