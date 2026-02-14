import pytest
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from dashboard.plots import create_price_chart, create_equity_curve, create_feature_importance_chart

def test_create_price_chart():
    df = pd.DataFrame({
        'Open': [100, 101, 102],
        'High': [102, 103, 104],
        'Low': [99, 100, 101],
        'Close': [101, 102, 103]
    }, index=pd.date_range("2023-01-01", periods=3))
    
    preds = np.array([101.5, 102.5, 103.5])
    
    fig = create_price_chart(df, preds)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 2 # Candlestick + Preds

def test_create_equity_curve():
    portfolio = pd.DataFrame({
        'PortfolioValue': [10000, 10100, 10200]
    }, index=pd.date_range("2023-01-01", periods=3))
    
    fig = create_equity_curve(portfolio)
    assert isinstance(fig, go.Figure)
    assert fig.data[0].y[0] == 10000

def test_create_feature_importance():
    importance = pd.DataFrame({
        'Feature': ['A', 'B'],
        'Importance': [0.6, 0.4]
    })
    
    fig = create_feature_importance_chart(importance)
    assert isinstance(fig, go.Figure)
    assert len(fig.data[0].x) == 2
