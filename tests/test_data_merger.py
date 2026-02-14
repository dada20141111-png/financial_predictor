import pytest
import pandas as pd
import numpy as np
from src.data_merger import DataMerger

def test_data_merger_alignment():
    # Target: Trades every day (Crypto style)
    dates_target = pd.date_range("2023-01-01", periods=5)
    target_df = pd.DataFrame({"Close": [100, 101, 102, 103, 104]}, index=dates_target)
    
    # Macro: Trades weekdays only (Stock style)
    # 2023-01-01 is Sunday -> NaN
    # 2023-01-02 is Monday -> Value
    dates_macro = pd.bdate_range("2023-01-01", periods=3) # Jan 2, 3, 4
    macro_df = pd.DataFrame({"Close": [50, 51, 52]}, index=dates_macro)
    
    merger = DataMerger()
    merged = merger.merge(target_df, {"Macro": macro_df})
    
    # Check shape
    assert len(merged) == 5
    assert "Macro" in merged.columns
    
    # Check Jan 1 (Sunday): Should be NaN initially. 
    # But since ffill starts from beginning, if Jan 1 is before first macro data, it stays NaN?
    # Actually ffill propagates LAST valid observation. If no valid observation before, it is NaN.
    # Jan 2 (Monday): Should match macro value 50
    assert merged.loc["2023-01-02", "Macro"] == 50.0
    
    # Check ffill behavior if we had data before.
    # Let's add a test case explicitly for gap filling.

def test_data_merger_ffill():
    # Target: T+0, T+1, T+2
    idx = pd.to_datetime(["2023-01-01", "2023-01-02", "2023-01-03"])
    target = pd.DataFrame({"Close": [1, 2, 3]}, index=idx)
    
    # Macro: Data only on T+0 and T+2. Missing T+1.
    idx_m = pd.to_datetime(["2023-01-01", "2023-01-03"])
    macro = pd.DataFrame({"Close": [10, 30]}, index=idx_m)
    
    merger = DataMerger()
    merged = merger.merge(target, {"M": macro})
    
    # T+1 should be filled with T+0 value (10)
    assert merged.loc["2023-01-02", "M"] == 10.0
    assert merged.loc["2023-01-03", "M"] == 30.0
