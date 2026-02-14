import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Ensure src is in path if running directly, though app.py handles this
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_provider import YahooFinanceProvider
from src.data_merger import DataMerger
from src.feature_engineering import TechnicalIndicatorTransformer
from src.market_analyzer import CorrelationTransformer
from src.xgboost_predictor import XGBoostPredictor
from src.backtesting import Backtester, PerformanceMetrics
from src.dashboard.layout import render_sidebar, render_metrics
from src.dashboard.plots import create_price_chart, create_equity_curve, create_feature_importance_chart

def run_dashboard():
    st.set_page_config(page_title="Financial Predictor AI", layout="wide")
    st.title("🤖 Financial Predictor AI Dashboard")
    
    config = render_sidebar()
    
    if st.sidebar.button("Run Analysis"):
        with st.spinner("Fetching Data & Running Model..."):
            try:
                # 1. Fetch Data
                provider = YahooFinanceProvider()
                merger = DataMerger()
                
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
                
                df_target = provider.fetch_history(config['symbol'], start=start_date, end=end_date)
                
                # Fetch Macros (simplified)
                macro_symbols = {"Gold": "GC=F", "VIX": "^VIX"}
                macro_data = {}
                for name, ticker in macro_symbols.items():
                    try:
                        macro_data[name] = provider.fetch_history(ticker, start=start_date, end=end_date)
                    except:
                        pass
                
                df_merged = merger.merge(df_target, macro_data)
                
                # 2. Features
                tech_transformer = TechnicalIndicatorTransformer()
                df_features = tech_transformer.transform(df_merged)
                
                corr_transformer = CorrelationTransformer()
                df_features = corr_transformer.transform(df_features, target_col='Close', window=config['window_size'])
                df_features.dropna(inplace=True)
                
                # 3. Model
                df_features['Target'] = df_features['Close'].shift(-1)
                working_df = df_features.dropna().copy()
                
                # Train/Test Split
                split_idx = int(len(working_df) * 0.8)
                train_df = working_df.iloc[:split_idx]
                test_df = working_df.iloc[split_idx:]
                
                feature_cols = [c for c in working_df.columns if c not in ['Target', 'Open', 'High', 'Low', 'Volume']]
                
                predictor = XGBoostPredictor()
                
                if config['enable_optimization'] and config['model_type'] == "XGBoost":
                     with st.spinner("Tuning Hyperparameters..."):
                        best_params = predictor.tune_hyperparameters(train_df[feature_cols], train_df['Target'], n_trials=20)
                        st.success(f"Optimized: LR={best_params.get('learning_rate', 'N/A')}")
                
                predictor.train(train_df[feature_cols], train_df['Target'])
                
                # Predict
                preds = predictor.predict(test_df[feature_cols])
                
                # 4. Backtest
                # Generate signals: If Prediction > Today Close -> Buy (1), else -> Cash (0)
                start_prices = test_df['Close']
                signals = np.where(preds > start_prices, 1, 0)
                signals_series = pd.Series(signals, index=test_df.index)
                
                # Backtester with config
                backtester = Backtester(initial_capital=config['initial_capital'], commission=config['commission'])
                results = backtester.run_backtest(signals_series, test_df['Close'])
                
                # Metrics
                metrics = PerformanceMetrics.calculate_metrics(results['PortfolioValue'])
                
                # --- Display ---
                render_metrics(metrics)
                
                st.subheader("Price vs Prediction (Test Set)")
                st.plotly_chart(create_price_chart(test_df, preds), use_container_width=True)
                
                st.subheader("Equity Curve")
                st.plotly_chart(create_equity_curve(results), use_container_width=True)
                
                st.subheader("Feature Importance")
                importance = predictor.get_feature_importance()
                st.plotly_chart(create_feature_importance_chart(importance), use_container_width=True)
                
                # Data Inspection
                with st.expander("View Backtest Data"):
                    st.dataframe(results)
                    
            except Exception as e:
                st.error(f"An error occurred: {e}")
                import traceback
                st.text(traceback.format_exc())
    else:
        st.info("Select parameters on the sidebar and click 'Run Analysis' to start.")

if __name__ == "__main__":
    run_dashboard()
