import pytest
import pandas as pd
import numpy as np
from src.market_analyzer import CorrelationTransformer, MarketAnalyzer

@pytest.fixture
def sample_market_data():
    dates = pd.date_range("2023-01-01", periods=100)
    # Asset A: Upward trend
    asset_a = np.linspace(100, 200, 100) + np.random.normal(0, 5, 100)
    # Asset B: Correlated with A
    asset_b = asset_a * 0.5 + np.random.normal(0, 2, 100)
    # Asset C: Inverse correlated
    asset_c = -asset_a + 500
    
    df = pd.DataFrame({
        "AssetA": asset_a,
        "AssetB": asset_b,
        "AssetC": asset_c
    }, index=dates)
    return df

def test_correlation_transformer(sample_market_data):
    transformer = CorrelationTransformer()
    df = transformer.transform(sample_market_data, target_col="AssetA", window=20)
    
    assert "Corr_AssetB_20" in df.columns
    assert "Corr_AssetC_20" in df.columns
    
    # Correlation with self should be avoided or 1.0. Our code skips target_col.
    assert "Corr_AssetA_20" not in df.columns
    
    # Check values
    # Asset B should have positive correlation
    last_corr_b = df["Corr_AssetB_20"].iloc[-1]
    assert last_corr_b > 0.5
    
    # Asset C should have negative correlation
    last_corr_c = df["Corr_AssetC_20"].iloc[-1]
    assert last_corr_c < -0.5

def test_lag_correlation(sample_market_data):
    analyzer = MarketAnalyzer()
    
    # Create a lagged relationship: AssetA follows AssetB by 2 days
    target = sample_market_data["AssetA"]
    feature = target.shift(2) # Feature happened 2 days ago
    
    # Fill NaN
    target = target.fillna(0)
    feature = feature.fillna(0)
    
    lags = analyzer.analyze_lag_correlation(target, feature, max_lag=5)
    
    # The correlation should be highest around lag 2?
    # Actually, if Feature is T-2, and we shift Feature by +2, it aligns with T.
    # Wait, let's verify logic. 
    # analyze_lag_correlation(target, feature) shifts feature by lag.
    # shifted_feature = feature.shift(lag).
    # If feature was already shifted (T-2), then feature.shift(2) becomes (T).
    # No, feature.shift(2) pushes data further into future.
    
    # Let's restart logic:
    # Feature X at time T. Target Y at time T+2.
    # Y.corr(X) is low.
    # Y.corr(X.shift(2))? 
    # X.shift(2) moves data from T to T+2.
    # So Y[T+2] matches X[T] (which is now at index T+2).
    # So yes, positive shift aligns past feature with future target.
    
    # Construct strictly:
    # Day 1: X=1
    # Day 3: Y=1
    # X = [1, 0, 0, ...], Y = [0, 0, 1, ...]
    # X.shift(2) = [NaN, NaN, 1, ...] -> matches Y.
    
    # In test:
    # feature = target.shift(2) means feature is a delayed version of target? 
    # No, feature[T] = target[T-2]. Feature is BEHIND target. Target leads.
    # So target[T] correlates with feature[T+2]? No.
    
    # Correct setup for "Feature leads Target":
    # feature[T] causes target[T+2].
    date_range = pd.date_range("2023-01-01", periods=100)
    feature_vals = np.random.randn(100)
    target_vals = np.roll(feature_vals, 2) # Target is feature shifted cleanly
    
    target_series = pd.Series(target_vals, index=date_range)
    feature_series = pd.Series(feature_vals, index=date_range)
    
    lags = analyzer.analyze_lag_correlation(target_series, feature_series, max_lag=5)
    
    # Lag 2 should be high (close to 1.0)
    assert lags[2] > 0.9
