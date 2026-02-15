import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.pattern_analyzer import EventPatternAnalyzer

class TestEventPatternAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = EventPatternAnalyzer()
        # Mock Memory
        self.analyzer.memory = MagicMock()
        # Mock Provider
        self.analyzer.provider = MagicMock()

    def test_analyze_impact(self):
        # Setup Mock Events
        mock_events = [
            {'date': '2023-01-01', 'description': 'Event 1', 'category': 'Test'},
            {'date': '2023-02-01', 'description': 'Event 2', 'category': 'Test'}
        ]
        self.analyzer.memory.get_events.return_value = mock_events
        
        # Setup Mock Price Data
        dates = pd.date_range(start='2023-01-01', end='2023-03-01')
        # simple linear price growth
        prices = [100 + i for i in range(len(dates))] 
        df = pd.DataFrame({'Close': prices}, index=dates)
        self.analyzer.provider.fetch_history.return_value = df
        
        # Run Analysis (Horizon 10 days)
        # Event 1: 2023-01-01 (Price 100) -> +10 days -> 2023-01-11 (Price 110) => +10%
        # Event 2: 2023-02-01 (Price 131) -> +10 days -> 2023-02-11 (Price 141) => +~7.6%
        
        result = self.analyzer.analyze_impact('BTC-USD', 'Test', horizon_days=10)
        
        self.assertNotIn('error', result)
        self.assertEqual(result['events_count'], 2)
        self.assertAlmostEqual(result['avg_return'], (0.10 + (141-131)/131) / 2, places=2)
        self.assertEqual(result['win_rate'], 1.0)

    def test_no_events(self):
        self.analyzer.memory.get_events.return_value = []
        result = self.analyzer.analyze_impact('BTC-USD', 'NonExistent', horizon_days=7)
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()
