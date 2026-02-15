import optuna
import pandas as pd
import numpy as np
from src.xgboost_predictor import XGBoostPredictor
from src.mlp_predictor import MLPPredictor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit

class ModelOptimizer:
    def __init__(self, X, y, n_trials=20):
        self.X = X
        self.y = y
        self.n_trials = n_trials

    def optimize_xgb(self):
        def objective(trial):
            param = {
                'n_estimators': trial.suggest_int('n_estimators', 50, 500),
                'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                'max_depth': trial.suggest_int('max_depth', 3, 10),
                'subsample': trial.suggest_float('subsample', 0.5, 1.0),
                'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
                'verbosity': 0
            }
            
            # TimeSeries Cross-Validation
            tscv = TimeSeriesSplit(n_splits=3)
            scores = []
            
            for train_index, test_index in tscv.split(self.X):
                X_train, X_test = self.X.iloc[train_index], self.X.iloc[test_index]
                y_train, y_test = self.y.iloc[train_index], self.y.iloc[test_index]
                
                model = XGBoostPredictor(**param)
                model.train(X_train, y_train)
                preds = model.predict(X_test)
                mse = mean_squared_error(y_test, preds)
                scores.append(mse)
                
            return np.mean(scores)

        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=self.n_trials)
        return study.best_params

    def optimize_mlp(self):
        def objective(trial):
            # Suggest hidden layer sizes
            n_layers = trial.suggest_int('n_layers', 1, 3)
            layers = []
            for i in range(n_layers):
                layers.append(trial.suggest_int(f'n_units_l{i}', 10, 100))
            
            param = {
                'hidden_layer_sizes': tuple(layers),
                'learning_rate_init': trial.suggest_float('learning_rate_init', 1e-4, 1e-1, log=True),
                'alpha': trial.suggest_float('alpha', 1e-5, 1e-1, log=True), # L2 penalty
                'max_iter': 500
            }
            
            tscv = TimeSeriesSplit(n_splits=3)
            scores = []
            
            for train_index, test_index in tscv.split(self.X):
                X_train, X_test = self.X.iloc[train_index], self.X.iloc[test_index]
                y_train, y_test = self.y.iloc[train_index], self.y.iloc[test_index]
                
                model = MLPPredictor(**param)
                model.train(X_train, y_train)
                preds = model.predict(X_test)
                mse = mean_squared_error(y_test, preds)
                scores.append(mse)
                
            return np.mean(scores)

        study = optuna.create_study(direction='minimize')
        study.optimize(objective, n_trials=self.n_trials)
        return study.best_params
