import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_price_chart(df: pd.DataFrame, preds: np.ndarray = None, title: str = "Price vs Prediction"):
    """
    Creates a candlestick chart with optional prediction overlay.
    """
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="OHLC"
    ))
    
    # Add Moving Averages if available
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], name="SMA 50", line=dict(color='orange', width=1)))
    if 'SMA_200' in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA_200'], name="SMA 200", line=dict(color='blue', width=1)))
        
    # Add Predictions
    if preds is not None:
        # Align predictions with DataFrame index
        # Assuming preds corresponds to df index
        if len(preds) == len(df):
            fig.add_trace(go.Scatter(
                x=df.index, 
                y=preds, 
                name="Prediction", 
                line=dict(color='purple', dash='dot', width=2)
            ))
            
    fig.update_layout(
        title=title,
        yaxis_title="Price",
        xaxis_title="Date",
        template="plotly_dark",
        height=600
    )
    return fig

def create_equity_curve(portfolio: pd.DataFrame, title: str = "Strategy Equity Curve"):
    """
    Creates an equity curve chart with drawdown visualization.
    """
    fig = go.Figure()
    
    # Portfolio Value
    fig.add_trace(go.Scatter(
        x=portfolio.index, 
        y=portfolio['PortfolioValue'], 
        name="Equity", 
        fill='tozeroy',
        line=dict(color='green')
    ))
    
    # Drawdown (optional, maybe on secondary y-axis or separate chart)
    # keeping it simple for now
    
    fig.update_layout(
        title=title,
        yaxis_title="Equity ($)",
        xaxis_title="Date",
        template="plotly_dark",
        height=500
    )
    return fig

def create_feature_importance_chart(importance, top_n: int = 15):
    """
    Creates a horizontal bar chart for feature importance.
    Accepts pd.Series (index=Feature, value=Score) or pd.DataFrame.
    """
    if isinstance(importance, pd.Series):
        importance = importance.reset_index()
        importance.columns = ['Feature', 'Importance']
    
    df_plot = importance.head(top_n).sort_values(by='Importance', ascending=True)
    
    fig = go.Figure(go.Bar(
        x=df_plot['Importance'],
        y=df_plot['Feature'],
        orientation='h',
        marker=dict(color='teal')
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Feature Importance",
        xaxis_title="Importance Score",
        yaxis_title="Feature",
        template="plotly_dark",
        height=500
    )
    return fig
