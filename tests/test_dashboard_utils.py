import pytest
import pandas as pd
import numpy as np

def get_okx_symbol(yahoo_symbol):
    symbol_map = {
        "BTC-USD": "BTC/USDT",
        "ETH-USD": "ETH/USDT",
        "SOL-USD": "SOL/USDT",
        "XRP-USD": "XRP/USDT"
    }
    return symbol_map.get(yahoo_symbol, "BTC/USDT")

def generate_signal(pred_price, current_price):
    return "BUY" if pred_price > current_price else "SELL"

def test_symbol_mapping():
    assert get_okx_symbol("BTC-USD") == "BTC/USDT"
    assert get_okx_symbol("ETH-USD") == "ETH/USDT"
    assert get_okx_symbol("UNKNOWN") == "BTC/USDT" # Default

def test_signal_generation():
    assert generate_signal(105, 100) == "BUY"
    assert generate_signal(95, 100) == "SELL"
    assert generate_signal(100.01, 100) == "BUY"
