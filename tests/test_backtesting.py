import pytest
import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from backtesting import Backtester, PerformanceMetrics

class TestPerformanceMetrics:
    def test_calculate_metrics_simple(self):
        # Create a simple portfolio value series
        # Day 0: 100
        # Day 1: 110 (+10%)
        # Day 2: 121 (+10%)
        # Day 3: 133.1 (+10%)
        values = pd.Series([100, 110, 121, 133.1])
        metrics = PerformanceMetrics.calculate_metrics(values)
        
        assert metrics['TotalReturn'] == pytest.approx(0.331, rel=1e-3)
        assert metrics['WinRateDaily'] == 1.0 # All days up
        assert metrics['MaxDrawdown'] == 0.0

    def test_calculate_metrics_drawdown(self):
        # 100 -> 50 -> 100
        values = pd.Series([100, 50, 100])
        metrics = PerformanceMetrics.calculate_metrics(values)
        
        assert metrics['MaxDrawdown'] == pytest.approx(-0.5, rel=1e-3)

class TestBacktester:
    def test_simple_buy_hold(self):
        # Price doubles: 100 -> 200
        # Signal: Buy on day 1 (index 0)
        prices = pd.Series([100.0, 200.0], index=pd.date_range("2023-01-01", periods=2))
        signals = pd.Series([1, 1], index=prices.index)
        
        # Commission 0 for simple math
        backtester = Backtester(initial_capital=10000.0, commission=0.0)
        results = backtester.run_backtest(signals, prices)
        
        # Day 1: Buy at 100. Cash -> 0, Position -> 100 shares. Value = 10000.
        # Day 2: Price 200. Position 100 shares. Value = 20000.
        assert results.iloc[0]['PortfolioValue'] == 10000.0
        assert results.iloc[1]['PortfolioValue'] == 20000.0
        assert results.iloc[1]['Position'] == 100.0

    def test_commission_impact(self):
        # Price constant: 100 -> 100
        # Signal: Buy
        prices = pd.Series([100.0, 100.0], index=pd.date_range("2023-01-01", periods=2))
        signals = pd.Series([1, 1], index=prices.index)
        
        # Commission 10%
        backtester = Backtester(initial_capital=10000.0, commission=0.1)
        results = backtester.run_backtest(signals, prices)
        
        # Day 1: Buy at 100.
        # Cash = 10000.
        # Shares = Cash / (Price * 1.1) = 10000 / 110 = 90.9090...
        # Cost = Shares * 100 * 0.1 = 909.09...
        # Value = 0 + (90.9090... * 100) = 9090.90...
        # Loss = Initial - Value = 909.09... which is roughly 9.1% (1/1.1)
        
        expected_shares = 10000.0 / 110.0
        assert results.iloc[0]['Position'] == pytest.approx(expected_shares)
        
        current_val = results.iloc[0]['PortfolioValue']
        assert current_val < 10000.0
