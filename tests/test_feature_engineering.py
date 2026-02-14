import pytest
import pandas as pd
import numpy as np
from src.feature_engineering import TechnicalIndicatorTransformer

@pytest.fixture
def sample_data():
    dates = pd.date_range("2023-01-01", periods=100)
    # Create somewhat trended data to verify indicators respond
    # Simple linear trend + noise
    close = np.linspace(100, 200, 100)
    df = pd.DataFrame({"Close": close}, index=dates)
    return df

def test_sma_calculation(sample_data):
    transformer = TechnicalIndicatorTransformer()
    transformed = transformer.transform(sample_data)
    
    assert "SMA_20" in transformed.columns
    assert "SMA_50" in transformed.columns
    
    # First 19 values should be NaN for SMA_20
    assert pd.isna(transformed["SMA_20"].iloc[18])
    assert not pd.isna(transformed["SMA_20"].iloc[19])

def test_macd_calculation(sample_data):
    transformer = TechnicalIndicatorTransformer()
    transformed = transformer.transform(sample_data)
    
    assert "MACD" in transformed.columns
    assert "MACD_Signal" in transformed.columns
    
    # MACD should be calculated for later values
    assert not pd.isna(transformed["MACD"].iloc[-1])

def test_rsi_calculation(sample_data):
    transformer = TechnicalIndicatorTransformer()
    transformed = transformer.transform(sample_data)
    
    assert "RSI" in transformed.columns
    
    # RSI should be between 0 and 100
    rsi = transformed["RSI"].dropna()
    assert ((rsi >= 0) & (rsi <= 100)).all()
