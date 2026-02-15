import streamlit as st
from datetime import datetime
from typing import Dict, Any

def render_sidebar():
    """Renders the sidebar and returns user configuration."""
    st.sidebar.header("Configuration")
    
    # Asset Selection
    asset_options = {
        "Crypto": ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"],
        "Tech Giants": ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META"],
        "Indices & ETFs": ["^GSPC", "^IXIC", "^DJI", "SPY", "QQQ", "GLD", "SLV"],
        "Custom": ["Enter Custom Symbol"]
    }
    
    selected_category = st.sidebar.selectbox("Asset Category", list(asset_options.keys()))
    
    if selected_category == "Custom":
        symbol = st.sidebar.text_input("Enter Asset Symbol (Yahoo Finance Ticker)", value="BTC-USD")
    else:
        symbol = st.sidebar.selectbox("Select Asset", asset_options[selected_category])
        
    model_type = st.sidebar.selectbox("Model Type", ["XGBoost", "MLP", "Linear Regression"])
    
    initial_capital = st.sidebar.number_input("Initial Capital ($)", value=10000.0)
    commission = st.sidebar.number_input("Commission Rate", value=0.001, format="%.4f")
    
    # Advanced Options
    with st.sidebar.expander("Advanced Settings"):
        enable_optimization = st.checkbox("Auto-Tune Hyperparameters (Slow)", value=False)
        window_size = st.slider("Lookback Window", 10, 100, 30)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("System Mode")
    data_source = st.sidebar.radio("Data Source", ["Yahoo Finance (Delayed)", "OKX (Real-time)"])
    trading_mode = st.sidebar.radio("Trading Mode", ["Backtest", "Paper Trading"])
        
    return {
        "symbol": symbol,
        "model_type": model_type,
        "initial_capital": initial_capital,
        "commission": commission,
        "enable_optimization": enable_optimization,
        "window_size": window_size,
        "data_source": data_source,
        "trading_mode": trading_mode
    }

def render_metrics(metrics: Dict[str, float]):
    """Renders key performance metrics in columns."""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Total Return", f"{metrics.get('TotalReturn', 0):.2%}")
    col2.metric("Sharpe Ratio", f"{metrics.get('SharpeRatio', 0):.2f}")
    col3.metric("Max Drawdown", f"{metrics.get('MaxDrawdown', 0):.2%}")
    col4.metric("Win Rate", f"{metrics.get('WinRateDaily', 0):.1%}")
    col5.metric("Sortino", f"{metrics.get('SortinoRatio', 0):.2f}")
