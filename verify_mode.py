from src.execution import OKXExecutor
from src.config import TRADING_MODE

print(f"Current TRADING_MODE in Config: {TRADING_MODE}")

try:
    executor = OKXExecutor()
    print(f"Executor Initialized Successfully.")
    print(f"Executor Mode: {executor.mode}")
    if executor.mode == 'mock':
        print("Mock Balance:", executor.get_balance('USDT'))
    elif executor.mode == 'testnet':
        print("Exchange Sandbox Enabled:", executor.exchange.sandbox)
except Exception as e:
    print(f"Executor Initialization Failed: {e}")
