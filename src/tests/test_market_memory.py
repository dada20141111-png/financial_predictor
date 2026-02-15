import unittest
import os
import json
import shutil
from src.market_memory import MarketMemory

class TestMarketMemory(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_data"
        self.mm = MarketMemory(data_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_add_and_retrieve_event(self):
        self.mm.add_event("2023-01-01", "Test Event", "Test", 0.5)
        events = self.mm.get_events("2023-01-01", "2023-01-02")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['description'], "Test Event")

    def test_date_range_filtering(self):
        self.mm.add_event("2023-01-01", "Event 1", "Test", 0.1)
        self.mm.add_event("2023-02-01", "Event 2", "Test", 0.1)
        self.mm.add_event("2023-03-01", "Event 3", "Test", 0.1)
        
        events = self.mm.get_events("2023-01-15", "2023-02-15")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['description'], "Event 2")

    def test_persistence(self):
        self.mm.add_event("2023-01-01", "Persistent Event", "Test", 0.5)
        
        # Reload from disk
        mm2 = MarketMemory(data_dir=self.test_dir)
        events = mm2.get_events("2023-01-01", "2023-01-01")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['description'], "Persistent Event")

if __name__ == '__main__':
    unittest.main()
