import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.data_provider import YahooFinanceProvider
from src.storage import StorageManager
from src.data_merger import DataMerger
from src.feature_engineering import TechnicalIndicatorTransformer
from src.market_analyzer import CorrelationTransformer, MarketAnalyzer
from src.model_lab import LinearRegressionPredictor, SimpleEvaluator
from src.xgboost_predictor import XGBoostPredictor

def run_pipeline(symbol: str, train: bool = True, use_xgboost: bool = True):
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
    macro_symbols = {
        "Gold": "GC=F",
        "Oil": "CL=F", 
        "TNX": "^TNX", # 10-Year Treasury Yield
        "VIX": "^VIX"
    }
    
    macro_data = {}
    for name, ticker in macro_symbols.items():
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
        print(f"Step 4: Training Model ({'XGBoost' if use_xgboost else 'Linear Regression'})...")
        
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
        
        if use_xgboost:
            predictor = XGBoostPredictor()
        else:
            predictor = LinearRegressionPredictor()
            
        predictor.train(X_train, y_train)
        
        # Evaluate
        preds = predictor.predict(X_test)
        evaluator = SimpleEvaluator()
        metrics = evaluator.evaluate(y_test, preds)
        print(f"  Evaluation Metrics: {metrics}")
        
        if use_xgboost:
            importance = predictor.get_feature_importance()
            print("\n  Top 5 Important Features:")
            print(importance.head(5))
            
        # Save
        model_name = f"{symbol}_{'xgb' if use_xgboost else 'lr'}.model"
        predictor.save(f"./data/{model_name}")
        print(f"  Model saved to ./data/{model_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, default="BTC-USD", help="Asset symbol")
    parser.add_argument("--model", type=str, default="xgb", choices=['xgb', 'lr'], help="Model type")
    args = parser.parse_args()
    
    run_pipeline(args.symbol, use_xgboost=(args.model == 'xgb'))
