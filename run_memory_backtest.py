from src.backtest_orchestrator import BacktestOrchestrator
import json

def main():
    print("Initializing Financial Predictor with Market Memory...")
    orchestrator = BacktestOrchestrator()
    
    # Analyze BTC for the last 1 Year
    symbol = "BTC-USD"
    period = "1Y"
    
    print(f"\n--- Running Backtest for {symbol} ({period}) ---")
    result = orchestrator.run_analysis(symbol, period)
    
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    perf = result['performance']
    events = result['events_during_period']
    
    print(f"\nResults for {result['dates'][0]} to {result['dates'][1]}")
    print(f"Total Return: {perf['total_return']*100:.2f}%")
    print(f"Final Value: ${perf['final_value']:,.2f}")
    
    print(f"\nKey Market Events ({len(events)}):")
    for evt in events:
        impact_icon = "[POS]" if evt['sentiment'] > 0 else "[NEG]" if evt['sentiment'] < 0 else "[NEU]"
        print(f"{evt['date']} {impact_icon} {evt['description']} ({evt['impact']})")

if __name__ == "__main__":
    main()
