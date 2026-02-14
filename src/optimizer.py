import optuna
import xgboost as xgb
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit

class Optimizer:
    """
    Hyperparameter optimizer using Optuna.
    """
    
    def __init__(self, n_trials: int = 20):
        self.n_trials = n_trials
        
    def optimize_xgboost(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """
        Run optimization for XGBoost.
        """
        def objective(trial):
            param = {
                'objective': 'reg:squarederror',
                'eval_metric': 'rmse',
                'booster': 'gbtree',
                'lambda': trial.suggest_float('lambda', 1e-8, 1.0, log=True),
                'alpha': trial.suggest_float('alpha', 1e-8, 1.0, log=True),
                'subsample': trial.suggest_float('subsample', 0.5, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
                'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                'max_depth': trial.suggest_int('max_depth', 3, 9),
                'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            }
            
            # Time Series Cross Validation
            tscv = TimeSeriesSplit(n_splits=3)
            scores = []
            
            for train_index, valid_index in tscv.split(X):
                X_train, X_valid = X.iloc[train_index], X.iloc[valid_index]
                y_train, y_valid = y.iloc[train_index], y.iloc[valid_index]
                
                model = xgb.XGBRegressor(**param)
                model.fit(X_train, y_train)
                preds = model.predict(X_valid)
                rmse = np.sqrt(mean_squared_error(y_valid, preds))
                scores.append(rmse)
                
            return np.mean(scores)

        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=self.n_trials)
        
        print(f"Best trial: {study.best_trial.value}")
        print(f"Best params: {study.best_trial.params}")
        
        return study.best_trial.params
