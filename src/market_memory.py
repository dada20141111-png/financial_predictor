import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class MarketMemory:
    """
    Manages historical market events, news, and macroeconomic data.
    Acts as a persistent memory for the financial predictor.
    """
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.memory_file = os.path.join(data_dir, "market_memory.json")
        self._ensure_storage()
        self.events = self._load_memory()

    def _ensure_storage(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        if not os.path.exists(self.memory_file):
            # Seed with empty list or initial data
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _load_memory(self) -> List[Dict]:
        """Load events from JSON storage."""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_memory(self):
        """Persist current events to disk."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=4, ensure_ascii=False)

    def add_event(self, date: str, description: str, category: str = "General", 
                  sentiment: float = 0.0, impact: str = "Neutral"):
        """
        Add a new market event.
        
        Args:
            date: YYYY-MM-DD format
            description: Description of the event
            category: e.g., 'Fed', 'Earnings', 'Geopolitics', 'Macro'
            sentiment: Float -1.0 to 1.0
            impact: Text description of expected impact (e.g., "Bullish for Tech")
        """
        new_event = {
            "id": f"evt_{len(self.events) + 1}_{datetime.now().timestamp()}",
            "date": date,
            "description": description,
            "category": category,
            "sentiment": sentiment,
            "impact": impact
        }
        self.events.append(new_event)
        # Sort by date
        self.events.sort(key=lambda x: x['date'])
        self.save_memory()
        print(f"Memory stored: [{date}] {description}")

    def get_events(self, start_date: str, end_date: str, category: str = None) -> List[Dict]:
        """Retrieve events within a date range."""
        results = []
        for event in self.events:
            if start_date <= event['date'] <= end_date:
                if category and event['category'] != category:
                    continue
                results.append(event)
        return results

    def get_all_events(self) -> List[Dict]:
        return self.events

if __name__ == "__main__":
    # Quick Test
    mm = MarketMemory()
    mm.add_event("2024-09-18", "Fed cuts rates by 50bps", "Fed", 0.8, "Bullish for Risk Assets")
    print(mm.get_events("2024-01-01", "2024-12-31"))
