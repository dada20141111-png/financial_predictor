import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class Backtester:
    """
    Simulates trading based on signals using an event-driven approach.
    Now supports commission and basic slippage simulation.
    """
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        """
        Args:
            initial_capital: Starting cash.
            commission: Transaction cost rate (e.g., 0.001 = 0.1%).
        """
        self.initial_capital = initial_capital
        self.commission = commission
        
    def run_backtest(self, signals: pd.Series, prices: pd.Series) -> pd.DataFrame:
        """
        Run backtest simulation.
        
        Args:
            signals: Series with 1 (Long), 0 (Cash/Neutral), -1 (Short - optional support).
                     Index must match prices. 
                     Note: Signal at index T is assumed to be executable at Close price of index T 
                     (idealized execution) or Open of T+1 depending on strategy. 
                     This implementation assumes idealized execution at Close of signal generation.
            prices: Series of asset prices.
            
        Returns:
            pd.DataFrame: Daily portfolio value, positions, and cash.
        """
        # Align signals and prices to ensure date match
        data = pd.DataFrame({'Price': prices, 'Signal': signals}).dropna()
        
        cash = self.initial_capital
        position = 0.0
        portfolio_values = []
        positions_history = []
        cash_history = []
        
        prev_pos = 0.0
        
        for date, row in data.iterrows():
            price = row['Price']
            signal = row['Signal']
            
            # Target position logic (1.0 = 100% invested, 0.0 = Cash)
            # This can be extended for partial sizing or leverage
            target_pos = float(signal)
            
            # Execute Trade if position changes
            if target_pos != prev_pos:
                # Calculate transaction
                
                # Going Long (Buy)
                if target_pos == 1.0 and prev_pos == 0.0:
                    # Buy max shares with available cash
                    # Cost = Price * Shares * (1 + Comm)
                    # Shares = Cash / (Price * (1 + Comm))
                    shares_to_buy = cash / (price * (1 + self.commission))
                    
                    cost = shares_to_buy * price * self.commission
                    position = shares_to_buy
                    cash = 0.0 # All in
                    
                # Going to Cash (Sell)
                elif target_pos == 0.0 and prev_pos == 1.0:
                    # Sell all shares
                    sale_value = position * price
                    cost = sale_value * self.commission
                    cash = sale_value - cost
                    position = 0.0
                
                # Handle other transitions (e.g. Short) if needed later
            
            # Mark to market for daily stats
            total_value = cash + (position * price)
            portfolio_values.append(total_value)
            positions_history.append(position)
            cash_history.append(cash)
            
            prev_pos = target_pos
            
        results = pd.DataFrame({
            'PortfolioValue': portfolio_values,
            'Position': positions_history,
            'Cash': cash_history
        }, index=data.index)
        
        return results

class PerformanceMetrics:
    """
    Calculates comprehensive performance metrics for a trading strategy.
    """
    
    @staticmethod
    def calculate_metrics(portfolio_values: pd.Series, risk_free_rate: float = 0.0) -> Dict[str, float]:
        """
        Calculate strategy performance metrics.
        
        Args:
            portfolio_values: Series of daily portfolio values.
            risk_free_rate: Annualized risk-free rate (decimal).
            
        Returns:
            Dictionary of metrics.
        """
        if len(portfolio_values) < 2:
            return {}

        # Daily Returns
        returns = portfolio_values.pct_change().dropna()
        
        # 1. Total Return
        total_return = (portfolio_values.iloc[-1] / portfolio_values.iloc[0]) - 1
        
        # 2. Annualized Volatility
        volatility = returns.std() * np.sqrt(252)
        
        # 3. Sharpe Ratio
        # Adjust risk-free rate to daily: (1 + r_annual)^(1/252) - 1 approx r_annual/252
        rf_daily = risk_free_rate / 252
        excess_returns = returns - rf_daily
        
        if returns.std() == 0:
            sharpe = 0.0
        else:
            sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252)
            
        # 4. Sortino Ratio (Downside Deviation)
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() * np.sqrt(252)
        
        if downside_std == 0:
            sortino = 0.0 if excess_returns.mean() <= 0 else np.inf
        else:
            sortino = (excess_returns.mean() * 252) / downside_std

        # 5. Max Drawdown
        cum_max = portfolio_values.cummax()
        drawdown = (portfolio_values - cum_max) / cum_max
        max_drawdown = drawdown.min()
        
        # 6. Calmar Ratio
        if max_drawdown == 0:
            calmar = np.inf
        else:
            calmar = (returns.mean() * 252) / abs(max_drawdown)
            
        # 7. Win Rate & Profit Factor (Trade-based analysis)
        # We need to infer trades from portfolio value changes or positions if available.
        # Since we only have portfolio values here, we approximate strictly based on daily returns.
        # For accurate trade stats, we'd need the trade log. 
        # Here we use "Winning Days" as a proxy for Win Rate.
        win_days = len(returns[returns > 0])
        total_days = len(returns)
        win_rate_daily = win_days / total_days if total_days > 0 else 0.0
        
        # Profit Factor (Gross Profit / Gross Loss) - Daily basis
        gross_profit = returns[returns > 0].sum()
        gross_loss = abs(returns[returns < 0].sum())
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else np.inf

        metrics = {
            "TotalReturn": total_return,
            "CAGR": ((portfolio_values.iloc[-1] / portfolio_values.iloc[0]) ** (252 / len(portfolio_values))) - 1 if len(portfolio_values) > 0 else 0.0,
            "Volatility": volatility,
            "SharpeRatio": sharpe,
            "SortinoRatio": sortino,
            "MaxDrawdown": max_drawdown,
            "CalmarRatio": calmar,
            "WinRateDaily": win_rate_daily,
            "ProfitFactorDaily": profit_factor
        }
        
        return metrics
