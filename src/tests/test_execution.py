
import pytest
import shutil
import os
import json
import pandas as pd
from unittest.mock import MagicMock
from src.execution import OKXExecutor, PositionManager

@pytest.fixture
def mock_env(tmp_path):
    # Setup clean data dir
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return str(data_dir)

def test_position_manager_basic(mock_env):
    pm = PositionManager(data_dir=mock_env)
    
    # 1. Check Initial Balance
    bal = pm.get_balance()
    assert bal['USDT'] == 10000.0
    
    # 2. Update Balance
    bal['USDT'] = 9000.0
    pm.save_balance(bal)
    assert pm.get_balance()['USDT'] == 9000.0
    
    # 3. Open Position (Buy)
    pm.update_position("BTC/USDT", "buy", 1.0, 50000.0, sl=49000.0, tp=55000.0)
    pos = pm.get_positions()
    assert "BTC/USDT" in pos
    assert pos["BTC/USDT"]['amount'] == 1.0
    assert pos["BTC/USDT"]['entry_price'] == 50000.0
    assert pos["BTC/USDT"]['sl'] == 49000.0
    
    # 4. Add to Position (Buy more) -> Check Avg Price
    pm.update_position("BTC/USDT", "buy", 1.0, 60000.0)
    pos = pm.get_positions()
    assert pos["BTC/USDT"]['amount'] == 2.0
    assert pos["BTC/USDT"]['entry_price'] == 55000.0 # (50k + 60k) / 2
    
    # 5. Sell Partial
    pm.update_position("BTC/USDT", "sell", 1.0, 60000.0)
    pos = pm.get_positions()
    assert pos["BTC/USDT"]['amount'] == 1.0
    
    # 6. Check History (Close/Sell should log PnL)
    hist = pm.get_history()
    assert len(hist) == 1
    # Sold 1.0 @ 60k. Entry was 55k. PnL = (60-55)*1 = 5000
    assert hist.iloc[0]['pnl'] == 5000.0

def test_okx_executor_paper(mock_env, monkeypatch):
    # Mock CCXT to avoid network calls
    executor = OKXExecutor(mode='paper')
    # Inject our temp data dir
    executor.pm = PositionManager(data_dir=mock_env)
    executor.simulated_balance = executor.pm.get_balance()
    
    # Mock exchange fetch_ticker
    mock_exchange = MagicMock()
    mock_exchange.fetch_ticker.return_value = {'last': 50000.0}
    executor.exchange = mock_exchange
    
    # Place Buy Order
    # Amount 0.1 BTC @ 50k = 5000 USDT cost
    res = executor.place_order("BTC/USDT", "buy", 0.1)
    
    assert res['status'] == 'closed'
    bal = executor.get_balance('USDT')
    assert bal == 5000.0 # 10000 - 5000
    
    pos = executor.get_positions()
    assert len(pos) == 1
    assert pos[0]['symbol'] == 'BTC/USDT'
    assert pos[0]['amount'] == 0.1
    
    # Place Sell Order (Profit)
    # Price moves to 60k
    mock_exchange.fetch_ticker.return_value = {'last': 60000.0}
    executor.place_order("BTC/USDT", "sell", 0.1)
    
    bal = executor.get_balance('USDT')
    # 5000 + (0.1 * 60000) = 5000 + 6000 = 11000
    assert bal == 11000.0
    
    hist = executor.get_trade_history()
    # 1 entry, 1 close
    assert len(hist) == 2 
    assert hist.iloc[1]['type'] == 'close'
    assert hist.iloc[1]['pnl'] == 1000.0 # (60k - 50k) * 0.1
