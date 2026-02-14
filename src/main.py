import argparse
import pandas as pd
from datetime import datetime, timedelta
from src.data_provider import YahooFinanceProvider
from src.storage import StorageManager
from src.feature_engineering import TechnicalIndicatorTransformer
from src.model_lab import LinearRegressionPredictor, SimpleEvaluator, TimeSeriesSplitter

def run_pipeline(symbol: str, train: bool = True):
    print(f"Starting pipeline for {symbol}...")
    
    # 1. Data Layer
    print("Step 1: Fetching Data...")
    provider = YahooFinanceProvider()
    storage = StorageManager("./data")
    
    # Try to load from storage first, or fetch meaningful history
    # For demo, we fetch fresh data for last 2 years
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    try:
        df = provider.fetch_history(symbol, start=start_date, end=end_date)
        storage.save_data(symbol, df)
        print(f"Data fetched: {len(df)} rows")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # 2. Feature Layer
    print("Step 2: Feature Engineering...")
    transformer = TechnicalIndicatorTransformer()
    df_features = transformer.transform(df)
    
    # Drop NaNs created by indicators
    df_features.dropna(inplace=True)
    print(f"Features created. Available columns: {df_features.columns.tolist()}")
    
    # 3. Model Layer
    if train:
        print("Step 3: Training Model...")
        # Prepare XY
        # Predict 5-day future return as target?
        # Or simple Next Day Return. Let's do Next Day Close for simplicity of this baseline.
        # Target: Next Day's Close
        df_features['Target'] = df_features['Close'].shift(-1)
        df_features.dropna(inplace=True)
        
        feature_cols = ['Close', 'SMA_20', 'SMA_50', 'RSI', 'MACD']
        X = df_features[feature_cols]
        y = df_features['Target']
        
        # Split (Simple Train/Test split for this demo, usually we use TimeSeriesSplit for validation)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
        
        predictor = LinearRegressionPredictor()
        predictor.train(X_train, y_train)
        
        # 4. Evaluation
        print("Step 4: Evaluating...")
        preds = predictor.predict(X_test)
        evaluator = SimpleEvaluator()
        metrics = evaluator.evaluate(y_test, preds)
        
        print(f"Evaluation Metrics: {metrics}")
        
        # Save model
        predictor.save(f"./data/{symbol}_model.pkl")
        print("Model saved.")
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", type=str, default="BTC-USD", help="Asset symbol")
    args = parser.parse_args()
    
    run_pipeline(args.symbol)
