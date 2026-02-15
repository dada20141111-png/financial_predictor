
# Centralized Configuration

# Macro Economic Symbols (Yahoo Finance Tickers)
MACRO_SYMBOLS = {
    # Existing
    "Gold": "GC=F",
    "Oil": "CL=F",
    "TNX": "^TNX",   # 10-Year Treasury Yield
    "VIX": "^VIX",   # Volatility Index
    
    # Metals (New)
    "Silver": "SI=F",
    "Copper": "HG=F",
    
    # Agriculture (New)
    "Corn": "ZC=F",
    "Soybean": "ZS=F",
    "Wheat": "ZW=F"
}

# Crypto Mapping (Yahoo -> OKX)
SYMBOL_MAP = {
    "BTC-USD": "BTC/USDT",
    "ETH-USD": "ETH/USDT",
    "SOL-USD": "SOL/USDT",
    "XRP-USD": "XRP/USDT",
    "BNB-USD": "BNB/USDT",
    "DOGE-USD": "DOGE/USDT",
    "ADA-USD": "ADA/USDT"
}

# Default training timeframe
DEFAULT_TRAINING_DAYS = 730 # 2 Years

# Trading Configuration
import os
from dotenv import load_dotenv
load_dotenv()

# Mode: 'mock' (Paper), 'testnet' (Sandbox), 'live' (Real)
TRADING_MODE = os.getenv('TRADING_MODE', 'mock').lower()

# Exchange Credentials
EXCHANGE_ID = 'okx' # Default to OKX, can be changed
API_KEY = os.getenv(f'{EXCHANGE_ID.upper()}_API_KEY')
SECRET_KEY = os.getenv(f'{EXCHANGE_ID.upper()}_SECRET_KEY')
PASSPHRASE = os.getenv(f'{EXCHANGE_ID.upper()}_PASSPHRASE')

print(f"Loaded Configuration: TRADING_MODE={TRADING_MODE}")
