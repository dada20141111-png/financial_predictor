import pytest
import pandas as pd
import numpy as np
import os
from src.model_lab import LinearRegressionPredictor, SimpleEvaluator, TimeSeriesSplitter

@pytest.fixture
def sample_data():
    X = pd.DataFrame({
        "Feature1": np.arange(100),
        "Feature2": np.arange(100) * 2
    }, index=pd.date_range("2023-01-01", periods=100))
    y = pd.Series(np.arange(100) * 3 + 5, index=X.index) # y = 3x + 5
    return X, y

def test_linear_regression_train_predict(sample_data):
    X, y = sample_data
    predictor = LinearRegressionPredictor()
    predictor.train(X, y)
    
    preds = predictor.predict(X)
    assert len(preds) == len(y)
    # Since it's a perfect linear relationship, error should be near 0
    assert np.allclose(preds, y, atol=1e-5)

def test_model_save_load(sample_data, tmp_path):
    X, y = sample_data
    predictor = LinearRegressionPredictor()
    predictor.train(X, y)
    
    save_path = tmp_path / "model.pkl"
    predictor.save(str(save_path))
    
    assert os.path.exists(save_path)
    
    new_predictor = LinearRegressionPredictor()
    new_predictor.load(str(save_path))
    
    preds = new_predictor.predict(X)
    assert np.allclose(preds, y, atol=1e-5)

def test_evaluator(sample_data):
    _, y = sample_data
    evaluator = SimpleEvaluator()
    # Perfect prediction
    metrics = evaluator.evaluate(y, y)
    assert metrics["MSE"] == 0.0
    assert metrics["R2"] == 1.0

def test_time_series_splitter(sample_data):
    X, _ = sample_data
    splitter = TimeSeriesSplitter(n_splits=3)
    splits = splitter.split(X)
    
    assert len(splits) == 3
    for train_idx, test_idx in splits:
        # Test should maintain temporal order: max(train) < min(test)
        assert max(train_idx) < min(test_idx)
