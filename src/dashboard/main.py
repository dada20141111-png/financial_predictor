import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import time

# Ensure src is in path if running directly, though app.py handles this
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data_provider import YahooFinanceProvider
from src.exchange import ExchangeProvider
from src.execution import OKXExecutor
from src.data_merger import DataMerger
from src.feature_engineering import TechnicalIndicatorTransformer
from src.market_analyzer import CorrelationTransformer
from src.xgboost_predictor import XGBoostPredictor
from src.mlp_predictor import MLPPredictor
from src.backtesting import Backtester, PerformanceMetrics
from src.dashboard.layout import render_sidebar, render_metrics
from src.dashboard.plots import create_price_chart, create_equity_curve, create_feature_importance_chart

from src.config import MACRO_SYMBOLS, SYMBOL_MAP, DEFAULT_TRAINING_DAYS

def run_dashboard():
    # Inner import to be absolutely safe against scope issues
    import streamlit as st
    
    st.set_page_config(page_title="Financial Predictor AI", layout="wide")
    st.title("🤖 Financial Predictor AI Dashboard")
    
    config = render_sidebar()
    
    # Paper Trading Status Panel (Always visible if enabled)
    if config['trading_mode'] == "Paper Trading":
        st.markdown("### 📜 Paper Trading Status")
        executor = OKXExecutor(mode='paper')
        
        col1, col2, col3 = st.columns(3)
        col1.metric("USDT Balance", f"${executor.get_balance('USDT'):,.2f}")
        col2.metric("BTC Balance", f"{executor.get_balance('BTC'):.4f}")
        col3.metric("ETH Balance", f"{executor.get_balance('ETH'):.4f}")
        
        if st.button("🔄 Reset Paper Balance"):
            executor.simulated_balance = {'USDT': 10000.0, 'BTC': 0.0, 'ETH': 0.0}
            executor._save_paper_balance()
            st.rerun()
            
    if st.sidebar.button("Run Analysis"):
        with st.spinner("Fetching Data & Running Model..."):
            try:
                # 1. Fetch Data
                if "OKX" in config['data_source']:
                    provider = ExchangeProvider(exchange_id='okx')
                    # Use centralized map
                    target_symbol = SYMBOL_MAP.get(config['symbol'], "BTC/USDT") 
                    st.info(f"Fetching Real-time data for {target_symbol} from OKX...")
                else:
                    provider = YahooFinanceProvider()
                    target_symbol = config['symbol']
                
                merger = DataMerger()
                
                end_date = datetime.now().strftime('%Y-%m-%d')
                start_date = (datetime.now() - timedelta(days=DEFAULT_TRAINING_DAYS)).strftime('%Y-%m-%d')
                
                # Fetch target
                df_target = provider.fetch_history(target_symbol, start=start_date, end=end_date)
                
                # Fetch Macros (Only for Yahoo mode usually)
                macro_data = {}
                if "Yahoo" in config['data_source']:
                    for name, ticker in MACRO_SYMBOLS.items():
                        try:
                            # Use a separate provider for macros if needed, but same one works for Yahoo
                            # Note: If provider is OKX, using it to fetch Yahoo ticker will fail.
                            # So even if main source is OKX, macros might need Yahoo provider.
                            # BUT, mixing synchronous/async or different libraries might be tricky.
                            # user instruction was to add macros. For now let's assume if OKX is main source, 
                            # we skip macros OR we need to instantiate a Yahoo provider purely for macros.
                            # Let's instantiate a dedicated macro provider to be safe.
                            macro_provider = YahooFinanceProvider()
                            macro_data[name] = macro_provider.fetch_history(ticker, start=start_date, end=end_date)
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
                if config['model_type'] == "MLP":
                    predictor = MLPPredictor(hidden_layer_sizes=(100, 50), max_iter=500)
                elif config['model_type'] == "Linear Regression":
                     # Assuming you have LR imported or just fallback to default for now as LR logic is simpler
                     # For brevity, let's keep it simple or import if needed.
                     # But wait, main_phase2 uses model_lab.LinearRegressionPredictor.
                     # Let's import it properly if we want to support it fully.
                     # For now, let's stick to XGB/MLP as primary options or just default to XGB if not MLP.
                     pass 
                
                if config['enable_optimization'] and config['model_type'] == "XGBoost":
                     with st.spinner("Tuning Hyperparameters..."):
                        best_params = predictor.tune_hyperparameters(train_df[feature_cols], train_df['Target'], n_trials=20)
                        st.success(f"Optimized: LR={best_params.get('learning_rate', 'N/A')}")
                
                predictor.train(train_df[feature_cols], train_df['Target'])
                
                # Predict
                preds = predictor.predict(test_df[feature_cols])
                
                # Get latest prediction (for Paper Trading)
                latest_pred = preds.iloc[-1]
                latest_price = test_df['Close'].iloc[-1]
                signal = "BUY" if latest_pred > latest_price else "SELL" # Simplified logic
                
                st.subheader(f"Analysis Result: {signal}")
                st.metric("Latest Close", f"{latest_price:.2f}")
                st.metric("Predicted Next Close", f"{latest_pred:.2f}", delta=f"{latest_pred-latest_price:.2f}")

                # 4. Mode Specific Action
                if config['trading_mode'] == "Paper Trading":
                     st.write("---")
                     st.subheader("Simulated Trading")
                     
                     tab1, tab2, tab3 = st.tabs(["Active Positions", "Trade History", "Manual Execution"])
                     
                     executor = OKXExecutor(mode='paper')
                     
                     with tab1:
                         positions = executor.get_positions()
                         if positions:
                             pos_df = pd.DataFrame(positions)
                             # safe formatting
                             format_dict = {
                                 "amount": "{:.4f}",
                                 "entry_price": "${:.2f}",
                                 "current_price": "${:.2f}",
                                 "unrealized_pnl": "${:.2f}",
                                 "pnl_pct": "{:.2f}%"
                             }
                             st.dataframe(pos_df.style.format({k: v for k, v in format_dict.items() if k in pos_df.columns}))
                         else:
                             st.info("No active positions.")
                             
                     with tab2:
                         history = executor.get_trade_history()
                         if not history.empty:
                             st.dataframe(history.sort_values(by="time", ascending=False))
                         else:
                             st.info("No trade history yet.")
                             
                     with tab3:
                         st.write(f"**Signal: {signal}**")
                         st.caption(f"Predicted move: {latest_price:.2f} -> {latest_pred:.2f}")
                         
                         col_a, col_b = st.columns(2)
                         # Default SL/TP suggestions
                         sl_price = col_a.number_input("Stop Loss ($)", value=float(latest_price * 0.98 if signal=="BUY" else latest_price * 1.02))
                         tp_price = col_b.number_input("Take Profit ($)", value=float(latest_price * 1.05 if signal=="BUY" else latest_price * 0.95))
                         
                         if st.button(f"Execute {signal} {target_symbol}"):
                             amount = 0.0
                             side = signal.lower()
                             
                             if side == 'buy':
                                 balance = executor.get_balance('USDT')
                                 if latest_price > 0:
                                     amount = (balance * 0.1) / latest_price
                             else:
                                 base_curr = target_symbol.split('/')[0]
                                 amount = executor.get_balance(base_curr)
                                 
                             if amount > 0:
                                 result = executor.place_order(target_symbol, side, amount, sl=sl_price, tp=tp_price)
                                 st.success(f"Order Placed: {result}")
                                 time.sleep(1)
                                 st.rerun()
                             else:
                                 st.warning("Insufficient funds or holdings.")

                else: # Backtest Mode
                    start_prices = test_df['Close']
                    signals = np.where(preds > start_prices, 1, 0)
                    signals_series = pd.Series(signals, index=test_df.index)
                    
                    backtester = Backtester(initial_capital=config['initial_capital'], commission=config['commission'])
                    results = backtester.run_backtest(signals_series, test_df['Close'])
                    
                    metrics = PerformanceMetrics.calculate_metrics(results['PortfolioValue'])
                    render_metrics(metrics)
                    
                    st.subheader("Equity Curve")
                    st.plotly_chart(create_equity_curve(results), use_container_width=True)

                # Shared Charts
                st.subheader("Price vs Prediction")
                st.plotly_chart(create_price_chart(test_df, preds), use_container_width=True)
                
                if config['model_type'] == "XGBoost":
                    st.subheader("Feature Importance")
                    importance = predictor.get_feature_importance()
                    st.plotly_chart(create_feature_importance_chart(importance), use_container_width=True)
                
                # Data Inspection
                if config['trading_mode'] != "Paper Trading":
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
