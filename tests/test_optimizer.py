import pytest
import pandas as pd
import numpy as np
from src.optimizer import Optimizer
from src.xgboost_predictor import XGBoostPredictor

@pytest.fixture
def sample_data():
    dates = pd.date_range("2023-01-01", periods=50)
    X = pd.DataFrame({
        "Feature1": np.random.randn(50),
        "Feature2": np.random.randn(50)
    }, index=dates)
    y = pd.Series(np.random.randn(50), index=dates)
    return X, y

def test_optimizer_runs(sample_data):
    X, y = sample_data
    # Use small n_trials for speed
    optimizer = Optimizer(n_trials=2)
    best_params = optimizer.optimize_xgboost(X, y)
    
    assert "learning_rate" in best_params
    assert "max_depth" in best_params
    assert best_params["max_depth"] >= 3

def test_xgboost_tuning_integration(sample_data):
    X, y = sample_data
    predictor = XGBoostPredictor()
    
    # Store initial params
    initial_lr = predictor.params["learning_rate"]
    
    # Tunes
    best_params = predictor.tune_hyperparameters(X, y, n_trials=1)
    
    # Check if params updated
    assert predictor.params == best_params
    # It's possible optuna chooses same LR, but unlikely to choose exactly 0.1 float if range is log space
    # unless 0.1 is exactly hit.
    
    # Check if we can train after tuning
    predictor.train(X, y)
    preds = predictor.predict(X)
    assert len(preds) == len(y)
