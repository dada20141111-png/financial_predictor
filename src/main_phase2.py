import argparse
import pandas as pd
import numpy as np
import sys
import os
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta

from src.data_provider import YahooFinanceProvider
from src.storage import StorageManager
from src.data_merger import DataMerger
from src.feature_engineering import TechnicalIndicatorTransformer
from src.market_analyzer import CorrelationTransformer, MarketAnalyzer
from src.model_lab import LinearRegressionPredictor, SimpleEvaluator
from src.xgboost_predictor import XGBoostPredictor
from src.mlp_predictor import MLPPredictor
from src.config import MACRO_SYMBOLS

def run_pipeline(symbol: str, train: bool = True, model_type: str = 'xgb', args=None):

    print(f"Starting Phase 2 Pipeline for {symbol}...")
    
    # --- 1. Data Layer (Enhanced) ---
    print("Step 1: Fetching Target & Macro Data...")
    provider = YahooFinanceProvider()
    storage = StorageManager("./data")
    merger = DataMerger()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    # Fetch Target
    df_target = provider.fetch_history(symbol, start=start_date, end=end_date)
    
    # Fetch Macros
    macro_data = {}
    for name, ticker in MACRO_SYMBOLS.items():
        try:
            print(f"  Fetching {name} ({ticker})...")
            df_macro = provider.fetch_history(ticker, start=start_date, end=end_date)
            macro_data[name] = df_macro
        except Exception as e:
            print(f"  Warning: Failed to fetch {name}: {e}")
            
    # Merge
    print("  Merging data...")
    df_merged = merger.merge(df_target, macro_data)
    print(f"  Merged Data Shape: {df_merged.shape}")
    
    # --- 2. Feature Layer (Enhanced) ---
    print("Step 2: Feature Engineering...")
    # Tech Indicators
    tech_transformer = TechnicalIndicatorTransformer()
    df_features = tech_transformer.transform(df_merged)
    
    # Correlation Features
    print("  Calculating Rolling Correlations...")
    corr_transformer = CorrelationTransformer()
    df_features = corr_transformer.transform(df_features, target_col='Close', window=30)
    
    # Drop NaNs
    df_features.dropna(inplace=True)
    
    # --- 3. Analysis Layer ---
    print("Step 3: Market Analysis...")
    analyzer = MarketAnalyzer()
    # Check correlation with Gold
    if "Gold" in df_features.columns:
        corr = df_features['Close'].corr(df_features['Gold'])
        print(f"  Overall Correlation with Gold: {corr:.4f}")
        
    # --- 4. Model Layer ---
    if train:
        print(f"Step 4: Training Model ({model_type.upper()})...")
        
        # Target: Next Day Close (Simple)
        df_features['Target'] = df_features['Close'].shift(-1)
        df_features.dropna(inplace=True)
        
        # Select Features (Auto-select numeric columns except Target)
        feature_cols = [c for c in df_features.columns if c not in ['Target', 'Open', 'High', 'Low', 'Volume']]
        # We keep Close as a feature (Auto-regressive)
        
        X = df_features[feature_cols]
        y = df_features['Target']
        
        # Split 80/20
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        if args.optimize:
            print("  Optimization Enabled: Tuning Hyperparameters with Optuna...")
            from src.optimization import ModelOptimizer
            optimizer = ModelOptimizer(X_train, y_train, n_trials=20)
            
            if model_type == 'xgb':
                 best_params = optimizer.optimize_xgb()
                 print(f"  Best XGB Params: {best_params}")
                 predictor = XGBoostPredictor(**best_params)
            elif model_type == 'mlp':
                 best_params = optimizer.optimize_mlp()
                 print(f"  Best MLP Params: {best_params}")
                 # Special handling for hidden_layer_sizes
                 hidden_layers = []
                 for k, v in best_params.items():
                     if k.startswith('n_units_l'):
                         hidden_layers.append(v)
                 # Re-construct tuple if needed, but the optimization.py returns struct params
                 # Actually optimize_mlp returns a dict. We need to parse it back to constructor args.
                 # Let's simplify: pass best_params directly if compatible, or map them.
                 # Re-instantiate with best params
                 # We need to reconstruct hidden_layer_sizes from n_units_l0, l1...
                 layers = [v for k, v in best_params.items() if k.startswith('n_units')]
                 # Sort by key to ensure order (l0, l1...)
                 sorted_layers = [best_params[k] for k in sorted(best_params.keys()) if k.startswith('n_units')]
                 
                 clean_params = {k: v for k, v in best_params.items() if not k.startswith('n_units') and not k.startswith('n_layers')}
                 clean_params['hidden_layer_sizes'] = tuple(sorted_layers)
                 
                 predictor = MLPPredictor(**clean_params)
            
        else:
            if model_type == 'xgb':
                predictor = XGBoostPredictor()
                print("  Selected Model: XGBoost (Default Params)")
            elif model_type == 'mlp':
                predictor = MLPPredictor(hidden_layer_sizes=(100, 50), max_iter=500)
                print("  Selected Model: MLP (Neural Network - Default Params)")
            else:
                predictor = LinearRegressionPredictor()
                print("  Selected Model: Linear Regression")
            
        predictor.train(X_train, y_train)
        
        # Sentiment Analysis (Real-time)
        print("step 4.5: Analyzing Market Sentiment...")
        try:
            from src.sentiment import SentimentAnalyzer
            from src.market_memory import MarketMemory # New Import
            
            # Use base symbol name for better news search (e.g. "BTC" instead of "BTC-USD")
            search_term = symbol.split('-')[0]
            sentiment_analyzer = SentimentAnalyzer(search_term)
            sentiment_score = sentiment_analyzer.analyze_sentiment()
            mood = sentiment_analyzer.get_market_mood(sentiment_score)
            print(f"  Current Sentiment for {search_term}: {sentiment_score:.4f} ({mood})")
            
            # --- Auto-Learning: Update Market Memory ---
            print("  Checking for significant market events...")
            top_event = sentiment_analyzer.extract_top_event()
            if top_event:
                mm = MarketMemory()
                # Check for duplicates today to avoid spamming
                today_str = datetime.now().strftime('%Y-%m-%d')
                existing_today = [e for e in mm.get_events(today_str, today_str) if e['description'] == top_event['description']]
                
                if not existing_today:
                    mm.add_event(
                        date=top_event['date'],
                        description=top_event['description'],
                        category=top_event['category'],
                        sentiment=top_event['sentiment'],
                        impact=top_event['impact']
                    )
                    print(f"  [MEMORY UPDATED] Added event: {top_event['description']}")
                else:
                    print("  Event already recorded today.")
            else:
                print("  No significant events to record.")
                
        except Exception as e:
            print(f"  Warning: Sentiment/Memory update failed: {e}")

        # Evaluate
        preds = predictor.predict(X_test)
        evaluator = SimpleEvaluator()
        metrics = evaluator.evaluate(y_test, preds)
        print(f"  Evaluation Metrics: {metrics}")
        
        if model_type == 'xgb':
            importance = predictor.get_feature_importance()
            print("\n  Top 5 Important Features:")
            print(importance.head(5))
            
        # Save
        model_name = f"{symbol}_{model_type}.model"
        predictor.save(f"./data/{model_name}")
        print(f"  Model saved to ./data/{model_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, default="BTC-USD", help="Asset symbol")
    parser.add_argument("--model", type=str, default="xgb", choices=['xgb', 'lr', 'mlp'], help="Model type")
    parser.add_argument("--optimize", action="store_true", help="Enable hyperparameter optimization")
    args = parser.parse_args()
    
    run_pipeline(args.symbol, model_type=args.model, args=args)
