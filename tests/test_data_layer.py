import pytest
import pandas as pd
import os
import shutil
from src.data_provider import YahooFinanceProvider
from src.storage import StorageManager

# Test DataProvider
def test_yahoo_provider_fetch():
    provider = YahooFinanceProvider()
    # Fetch a small range of data for a stable ticker
    df = provider.fetch_history("SPY", "2023-01-01", "2023-01-10")
    
    assert not df.empty
    assert isinstance(df.index, pd.DatetimeIndex)
    assert "Close" in df.columns
    # Check if we got expected number of rows (trading days)
    # Jan 1 was Sunday, Jan 2 observed holiday (sometimes). 
    # Just checking we got > 0 rows is strict enough for connectivity test.
    assert len(df) > 0

def test_yahoo_provider_invalid_symbol():
    provider = YahooFinanceProvider()
    # Expect empty or error. detailed behavior depends on yfinance version, 
    # but our wrapper raises ValueError on empty
    with pytest.raises(ValueError):
        provider.fetch_history("INVALID_SYMBOL_XYZ", "2023-01-01", "2023-01-10")

# Test StorageManager
@pytest.fixture
def temp_storage():
    test_dir = "./test_data"
    manager = StorageManager(test_dir)
    yield manager
    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_storage_save_load(temp_storage):
    symbol = "TEST"
    df = pd.DataFrame({"Close": [100, 101, 102]}, index=pd.date_range("2023-01-01", periods=3))
    
    temp_storage.save_data(symbol, df)
    
    assert temp_storage.exists(symbol)
    
    loaded_df = temp_storage.load_data(symbol)
    # Parquet does not preserve index frequency, so we ignore it
    pd.testing.assert_frame_equal(df, loaded_df, check_freq=False)

def test_storage_not_found(temp_storage):
    assert temp_storage.load_data("NONEXISTENT") is None
