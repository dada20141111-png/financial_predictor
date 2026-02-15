from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, List, Optional
from src.backtesting import Backtester
from src.market_memory import MarketMemory
from src.data_provider import YahooFinanceProvider

class BacktestOrchestrator:
    """
    Orchestrates backtests over specific time periods and correlates
    results with historical market memory.
    """
    def __init__(self):
        self.memory = MarketMemory()
        self.provider = YahooFinanceProvider()
        self.backtester = Backtester()

    def _get_date_range(self, period_type: str, custom_end: datetime = None) -> tuple[str, str]:
        """
        Calculate start and end dates based on period type.
        types: '1W', '1M', '3M', '6M', '1Y', 'YTD'
        """
        end_dt = custom_end if custom_end else datetime.now()
        
        if period_type == '1W':
            start_dt = end_dt - timedelta(weeks=1)
        elif period_type == '1M':
            start_dt = end_dt - timedelta(days=30)
        elif period_type == '3M':
            start_dt = end_dt - timedelta(days=90)
        elif period_type == '6M':
            start_dt = end_dt - timedelta(days=180)
        elif period_type == '1Y':
            start_dt = end_dt - timedelta(days=365)
        elif period_type == 'YTD':
            start_dt = datetime(end_dt.year, 1, 1)
        else:
            raise ValueError(f"Unknown period type: {period_type}")
            
        return start_dt.strftime('%Y-%m-%d'), end_dt.strftime('%Y-%m-%d')

    def run_analysis(self, symbol: str, period_type: str) -> Dict:
        """
        Run backtest for a symbol over a period and attach memory events.
        """
        start_date, end_date = self._get_date_range(period_type)
        print(f"Running analysis for {symbol} | {period_type} | {start_date} to {end_date}")
        
        # 1. Fetch Data
        try:
            df = self.provider.fetch_history(symbol, start_date, end_date)
        except Exception as e:
            return {"error": f"Data fetch failed: {str(e)}"}

        if df.empty:
            return {"error": "No data found for period"}

        # 2. Generate Signals (Simple Strategy for Demo)
        # Strategy: Buy and Hold (Signal = 1 throughout)
        # TODO: Inject real strategies here
        signals = pd.Series(1, index=df.index) 
        
        # 3. Run Backtest
        results = self.backtester.run_backtest(signals, df['Close'])
        
        # 4. Calculate Perf
        # We need a PerfMetrics class or method. 
        # Using existing one from backtesting.py if available or computing manually
        total_return = (results['PortfolioValue'].iloc[-1] / results['PortfolioValue'].iloc[0]) - 1
        
        # 5. Get Events
        events = self.memory.get_events(start_date, end_date)
        
        return {
            "symbol": symbol,
            "period": period_type,
            "dates": (start_date, end_date),
            "performance": {
                "total_return": total_return,
                "final_value": results['PortfolioValue'].iloc[-1]
            },
            "events_during_period": events,
            # "daily_data": results  # Return/Save full data if needed
        }

if __name__ == "__main__":
    orch = BacktestOrchestrator()
    # Test with recent data (ensure data is available)
    res = orch.run_analysis("BTC-USD", "1M")
    print(json.dumps(res, indent=2, default=str))
