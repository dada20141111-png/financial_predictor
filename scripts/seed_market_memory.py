import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.market_memory import MarketMemory

def seed_data():
    mm = MarketMemory()
    
    # Check if already seeded (simple check)
    existing = mm.get_all_events()
    if len(existing) > 10:
        print("Memory appears to be already seeded.")
        return

    events = [
        # 2020
        ("2020-03-15", "Fed cuts to zero, launches QE infinity", "Fed", 0.9, "Bullish for Assets"),
        ("2020-05-11", "Bitcoin Halving", "Crypto", 1.0, "Bullish"),
        ("2020-11-03", "US Residential Election 2020", "Politics", 0.0, "High Volatility"),
        
        # 2021
        ("2021-02-08", "Tesla buys $1.5B Bitcoin", "Crypto", 1.0, "Bullish"),
        ("2021-04-14", "Coinbase IPO", "Crypto", 0.8, "Short-term Bullish"),
        ("2021-05-19", "China bans crypto mining", "Regulation", -1.0, "Bearish Crash"),
        ("2021-11-10", "US CPI hits 6.2%, highest in 30 years", "Macro", -0.5, "Inflation Fears"),
        
        # 2022
        ("2022-03-16", "Fed starts hiking cycle (25bps)", "Fed", -0.2, "Liquidity Tightening"),
        ("2022-05-09", "Terra/LUNA collapse", "Crypto", -1.0, "Systemic Crash"),
        ("2022-06-15", "Fed hikes 75bps", "Fed", -0.8, "Bearish"),
        ("2022-11-08", "FTX Collapse", "Crypto", -1.0, "Market Crash"),
        
        # 2023
        ("2023-03-10", "SVB Bank Failure", "Macro", -0.5, "Banking Crisis"),
        ("2023-06-14", "Fed pauses hikes", "Fed", 0.3, "Stabilization"),
        
        # 2024
        ("2024-01-10", "SEC approves Bitcoin spot ETFs", "Crypto", 1.0, "Institutional Adoption"),
        ("2024-04-19", "Bitcoin Halving 2024", "Crypto", 1.0, "Long-term Bullish"),
        ("2024-09-18", "Fed cuts rates by 50bps", "Fed", 0.8, "Bullish for Risk Assets"),
        ("2024-11-05", "US Presidential Election 2024", "Politics", 0.2, "Volatility"),
        
        # 2025 (Simulated Future History)
        ("2025-02-15", "Crypto Market Cap hits $5T", "Crypto", 1.0, "Historic High"),
        ("2025-06-20", "Global Central Banks Coordinate Rate Cuts", "Macro", 0.9, "Liquidity Boost"),
        ("2025-10-10", "Major Tech Regulation Bill Passed", "Regulation", -0.4, "Tech Correction"),
        
        # 2026 (Current Year)
        ("2026-01-05", "Bitcoin breaks $150k barrier", "Crypto", 1.0, "Euphoria"),
        ("2026-02-01", "Fed signals neutral rate achieved", "Fed", 0.5, "Stability")
    ]

    print(f"Seeding {len(events)} events...")
    for date, desc, cat, sent, impact in events:
        mm.add_event(date, description=desc, category=cat, sentiment=sent, impact=impact)
    
    print("Done.")

if __name__ == "__main__":
    seed_data()
