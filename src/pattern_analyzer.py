import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.market_memory import MarketMemory
from src.data_provider import YahooFinanceProvider

class EventPatternAnalyzer:
    """
    Analyzes how asset prices behave following specific types of market events.
    """
    def __init__(self):
        self.memory = MarketMemory()
        self.provider = YahooFinanceProvider()

    def analyze_impact(self, symbol: str, category: str, horizon_days: int = 7) -> Dict:
        """
        Calculate statistical impact of event category on asset price over a horizon.
        
        Args:
            symbol: Asset symbol (e.g., 'BTC-USD')
            category: Event category (e.g., 'Fed', 'Crypto')
            horizon_days: Number of days to look ahead (default 7)
            
        Returns:
            Dict containing stats (avg_return, win_rate, events_analyzed)
        """
        # 1. Get all events of category (past only)
        # We limit to events older than horizon_days to ensure we have outcome data
        cutoff_date = (datetime.now() - timedelta(days=horizon_days)).strftime('%Y-%m-%d')
        all_events = self.memory.get_events("2000-01-01", cutoff_date, category=category)
        
        if not all_events:
            return {"error": "No historical events found for this category."}

        # 2. Fetch Data for relevant periods
        # To be efficient, we might fetch the full history once if events span a long time
        # Or fetch chunks. Let's fetch full history for simplicity given our data scale.
        try:
            # Find range
            start_date = all_events[0]['date']
            end_date = datetime.now().strftime('%Y-%m-%d')
            # Buffer start date by a few days to be safe
            start_buffer = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=5)).strftime('%Y-%m-%d')
            
            df = self.provider.fetch_history(symbol, start=start_buffer, end=end_date)
            df.index = pd.to_datetime(df.index)
        except Exception as e:
            return {"error": f"Data fetch failed: {e}"}

        # 3. Calculate Returns
        returns = []
        detailed_results = []
        
        for event in all_events:
            evt_date = pd.to_datetime(event['date'])
            
            # Find price at event date (or closest after)
            try:
                # specific loc logic
                if evt_date not in df.index:
                    # Find nearest next trading day
                    # method='bfill' in get_indexer or searchsorted
                    idx_loc = df.index.searchsorted(evt_date)
                    if idx_loc >= len(df):
                        continue
                    start_price = df['Close'].iloc[idx_loc]
                    start_actual_date = df.index[idx_loc]
                else:
                    start_price = df.loc[evt_date]['Close']
                    start_actual_date = evt_date

                # Find price at Horizon
                target_date = start_actual_date + timedelta(days=horizon_days)
                
                # Check if target date is within range
                if target_date > df.index[-1]:
                    continue
                    
                # Find nearest for target
                if target_date not in df.index:
                    idx_loc = df.index.searchsorted(target_date)
                    if idx_loc >= len(df):
                        continue
                    end_price = df['Close'].iloc[idx_loc]
                else:
                    end_price = df.loc[target_date]['Close']
                
                # Calculate Pct Change
                pct_change = (end_price - start_price) / start_price
                returns.append(pct_change)
                
                detailed_results.append({
                    "date": event['date'],
                    "description": event['description'],
                    "return": pct_change
                })
                
            except Exception as e:
                # Date lookup might fail if market closed etc, skip
                continue

        if not returns:
            return {"error": "Insufficient price data for events."}

        # 4. Compute Stats
        avg_return = np.mean(returns)
        median_return = np.median(returns)
        win_rate = len([r for r in returns if r > 0]) / len(returns)
        
        return {
            "category": category,
            "horizon_days": horizon_days,
            "events_count": len(returns),
            "avg_return": avg_return,
            "median_return": median_return,
            "win_rate": win_rate,
            "min_return": np.min(returns),
            "max_return": np.max(returns),
            "std_dev": np.std(returns),
            "details": detailed_results
        }
