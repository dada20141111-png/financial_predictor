
import pytest
import pandas as pd
import numpy as np
import os
from src.mlp_predictor import MLPPredictor

@pytest.fixture
def sample_data():
    # Create synthetic data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    df = pd.DataFrame({
        'Feature1': np.random.rand(100),
        'Feature2': np.random.rand(100) * 100,
        'Feature3': np.random.randint(0, 2, 100)
    }, index=dates)
    
    # Target: linear combination + noise
    y = 2 * df['Feature1'] + 0.5 * df['Feature2'] + np.random.normal(0, 0.1, 100)
    
    return df, y

def test_mlp_initialization():
    predictor = MLPPredictor(hidden_layer_sizes=(10, 5), max_iter=100)
    assert predictor.hidden_layer_sizes == (10, 5)
    assert predictor.is_fitted is False

def test_mlp_train_predict(sample_data):
    X, y = sample_data
    
    predictor = MLPPredictor(hidden_layer_sizes=(10,), max_iter=500, random_state=42)
    predictor.train(X, y)
    
    assert predictor.is_fitted is True
    
    # Predict
    preds = predictor.predict(X)
    assert len(preds) == len(X)
    assert isinstance(preds, pd.Series)
    assert not preds.isna().any()

def test_mlp_save_load(sample_data, tmp_path):
    X, y = sample_data
    save_path = tmp_path / "mlp_model.pkl"
    
    predictor = MLPPredictor(hidden_layer_sizes=(5,), max_iter=100)
    predictor.train(X, y)
    preds_orig = predictor.predict(X)
    
    predictor.save(str(save_path))
    assert os.path.exists(save_path)
    
    # New instance
    predictor_loaded = MLPPredictor()
    assert predictor_loaded.is_fitted is False
    
    predictor_loaded.load(str(save_path))
    assert predictor_loaded.is_fitted is True
    
    preds_loaded = predictor_loaded.predict(X)
    
    # Check equality
    pd.testing.assert_series_equal(preds_orig, preds_loaded)

def test_predict_before_train_raises_error(sample_data):
    X, _ = sample_data
    predictor = MLPPredictor()
    
    with pytest.raises(RuntimeError):
        predictor.predict(X)
