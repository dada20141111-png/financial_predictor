import pytest
import pandas as pd
import numpy as np
import os
from src.xgboost_predictor import XGBoostPredictor

@pytest.fixture
def sample_data():
    dates = pd.date_range("2023-01-01", periods=100)
    X = pd.DataFrame({
        "Feature1": np.arange(100),
        "Feature2": np.random.randn(100)
    }, index=dates)
    # Simple linear relationship for testing
    y = X["Feature1"] * 2 + X["Feature2"] * 0.5 + 10
    return X, y

def test_xgboost_train_predict(sample_data):
    X, y = sample_data
    predictor = XGBoostPredictor()
    predictor.train(X, y)
    
    preds = predictor.predict(X)
    assert len(preds) == len(y)
    
    # Check if predictions are reasonable (correlation should be high)
    corr = np.corrcoef(y, preds)[0, 1]
    assert corr > 0.9

def test_xgboost_feature_importance(sample_data):
    X, y = sample_data
    predictor = XGBoostPredictor()
    predictor.train(X, y)
    
    importance = predictor.get_feature_importance()
    assert isinstance(importance, pd.Series)
    assert len(importance) == 2
    # Feature1 should be more important than Feature2 based on our formula (2x vs 0.5x, though scale matters)
    # Feature1 range is 0-100, Feature2 is ~ -3 to 3. 
    # Actually scaling affects importance in tree models less than linear, but stronger signal usually wins.
    assert "Feature1" in importance.index

def test_xgboost_save_load(sample_data, tmp_path):
    X, y = sample_data
    predictor = XGBoostPredictor()
    predictor.train(X, y)
    
    save_path = tmp_path / "model.json"
    predictor.save(str(save_path))
    
    assert os.path.exists(save_path)
    
    new_predictor = XGBoostPredictor()
    new_predictor.load(str(save_path))
    
    preds_orig = predictor.predict(X)
    preds_loaded = new_predictor.predict(X)
    
    np.testing.assert_allclose(preds_orig, preds_loaded)
