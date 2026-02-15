from abc import ABC, abstractmethod
import ccxt
from typing import Dict, Any, Optional, List
import os
from dotenv import load_dotenv
import json
import time
import pandas as pd
from datetime import datetime
from pathlib import Path

# Load env
load_dotenv()

class ExecutionEngine(ABC):
    """
    Abstract base class for trade execution.
    """
    
    @abstractmethod
    def get_balance(self, asset: str) -> float:
        """Get available balance for an asset."""
        pass
        
    @abstractmethod
    def place_order(self, symbol: str, side: str, amount: float, order_type: str = 'market', price: float = None, sl: float = None, tp: float = None) -> Dict[str, Any]:
        """
        Place an order with optional SL/TP.
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get list of active positions."""
        pass
        
    @abstractmethod
    def get_trade_history(self) -> pd.DataFrame:
        """Get transaction history."""
        pass

class PositionManager:
    """
    Manages local paper trading positions and history.
    """
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.positions_file = os.path.join(data_dir, "paper_positions.json")
        self.history_file = os.path.join(data_dir, "trade_history.csv")
        self.balance_file = os.path.join(data_dir, "paper_balance.json")
        
    def get_balance(self) -> Dict[str, float]:
        if os.path.exists(self.balance_file):
            try:
                with open(self.balance_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'USDT': 10000.0, 'BTC': 0.0, 'ETH': 0.0}

    def save_balance(self, balance: Dict[str, float]):
        with open(self.balance_file, 'w') as f:
            json.dump(balance, f, indent=4)

    def get_positions(self) -> Dict[str, Dict]:
        if os.path.exists(self.positions_file):
            try:
                with open(self.positions_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_positions(self, positions: Dict[str, Dict]):
        with open(self.positions_file, 'w') as f:
            json.dump(positions, f, indent=4)
            
    def log_trade(self, trade: Dict[str, Any]):
        """Append trade to CSV history."""
        df_new = pd.DataFrame([trade])
        if os.path.exists(self.history_file):
            df_new.to_csv(self.history_file, mode='a', header=False, index=False)
        else:
            df_new.to_csv(self.history_file, index=False)

    def get_history(self) -> pd.DataFrame:
        if os.path.exists(self.history_file):
            return pd.read_csv(self.history_file)
        return pd.DataFrame(columns=['id', 'time', 'symbol', 'side', 'amount', 'price', 'cost', 'pnl', 'type'])

    def update_position(self, symbol: str, side: str, amount: float, price: float, sl: float = None, tp: float = None):
        positions = self.get_positions()
        
        if side == 'buy':
            # Long position logic (Simple: Average entry price)
            if symbol not in positions:
                positions[symbol] = {
                    'amount': 0.0, 'entry_price': 0.0, 'sl': sl, 'tp': tp
                }
            
            pos = positions[symbol]
            total_cost = (pos['amount'] * pos['entry_price']) + (amount * price)
            new_amount = pos['amount'] + amount
            new_avg_price = total_cost / new_amount if new_amount > 0 else 0.0
            
            pos['amount'] = new_amount
            pos['entry_price'] = new_avg_price
            if sl: pos['sl'] = sl
            if tp: pos['tp'] = tp
            
        elif side == 'sell':
            # Reducing/Closing position
            if symbol in positions:
                pos = positions[symbol]
                # Calculate Realized PnL
                # Sell Price - Entry Price
                pnl = (price - pos['entry_price']) * amount
                
                # Log this 'closing' trade with PnL
                self.log_trade({
                    'id': f"trade_{int(time.time())}",
                    'time': datetime.now().isoformat(),
                    'symbol': symbol,
                    'side': 'sell',
                    'amount': amount,
                    'price': price,
                    'cost': amount * price,
                    'pnl': pnl,
                    'type': 'close' if amount >= pos['amount'] else 'reduce'
                })
                
                pos['amount'] -= amount
                if pos['amount'] <= 1e-6: # Float tolerance
                    del positions[symbol]
        
        self.save_positions(positions)

class OKXExecutor(ExecutionEngine):
    """
    Executor implementation for OKX with 3 modes:
    1. 'mock': Local paper trading (Safe).
    2. 'testnet': Exchange Sandbox (Needs Keys).
    3. 'live': Real Trading (Risk).
    """
    
    def __init__(self):
        from src.config import TRADING_MODE, API_KEY, SECRET_KEY, PASSPHRASE
        self.mode = TRADING_MODE
        
        print(f"Initializing Executor in [{self.mode.upper()}] mode...")
        
        # 1. Mock Mode (Paper Trading)
        if self.mode == 'mock':
            self.pm = PositionManager()
            self.simulated_balance = self.pm.get_balance()
            self.exchange = None
            
        # 2. Network Modes (Testnet/Live)
        else:
            if not (API_KEY and SECRET_KEY and PASSPHRASE):
                raise ValueError(f"API Keys missing for {self.mode} mode! Check .env")
            
            self.exchange = ccxt.okx({
                'apiKey': API_KEY,
                'secret': SECRET_KEY,
                'password': PASSPHRASE,
                'enableRateLimit': True,
            })
            
            if self.mode == 'testnet':
                self.exchange.set_sandbox_mode(True)
                print("  -> Sandbox Mode Enabled")
        
    def get_balance(self, asset: str) -> float:
        if self.mode == 'mock':
            return self.simulated_balance.get(asset, 0.0)
            
        try:
            balance = self.exchange.fetch_balance()
            return balance['free'].get(asset, 0.0)
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return 0.0
            
    def get_positions(self) -> List[Dict[str, Any]]:
        if self.mode == 'mock':
            raw_pos = self.pm.get_positions()
            pos_list = []
            for symbol, data in raw_pos.items():
                # Mock current price fetch (or use latest if available)
                current_price = data['entry_price'] # Placeholder
                pos_list.append({
                    'symbol': symbol,
                    'amount': data['amount'],
                    'entry_price': data['entry_price'],
                    'current_price': current_price,
                    'unrealized_pnl': 0, # Placeholder
                    'pnl_pct': 0,
                    'sl': data.get('sl'),
                    'tp': data.get('tp')
                })
            return pos_list
        else:
            try:
                # CCXT unified position fetching
                positions = self.exchange.fetch_positions()
                # Transform to our format
                # Note: This schema varies by exchange, simplified here
                return positions 
            except Exception as e:
                print(f"Error fetching positions: {e}")
                return []

    def get_trade_history(self) -> pd.DataFrame:
        if self.mode == 'mock':
            return self.pm.get_history()
        # For live, we could fetch from exchange, but for now return empty or implement log
        return pd.DataFrame()

    def place_order(self, symbol: str, side: str, amount: float, order_type: str = 'market', price: float = None, sl: float = None, tp: float = None) -> Dict[str, Any]:
        """
        Places an order based on current mode.
        """
        # --- MOCK MODE ---
        if self.mode == 'mock':
            print(f"[MOCK] Placing {side.upper()} order for {amount} {symbol}")
            
            try:
                base, quote = symbol.split('/')
            except ValueError:
                return {'status': 'failed', 'error': 'Invalid symbol format'}
            
            # Simulated Execution logic (same as old paper mode)
            # Use fixed dummy price if strictly mocking to avoid network calls, 
            # OR try to fetch ticker if we want realistic mock
            exec_price = price if price else 50000.0 # Default fallback
            
            cost = amount * exec_price
            
            # Simple balance check
            if side == 'buy':
                if self.simulated_balance.get(quote, 0) >= cost:
                    self.simulated_balance[quote] -= cost
                    self.simulated_balance[base] = self.simulated_balance.get(base, 0) + amount
                    self.pm.save_balance(self.simulated_balance)
                    self.pm.update_position(symbol, 'buy', amount, exec_price, sl, tp)
                    
                    # Log
                    self.pm.log_trade({
                        'id': f"mock_{int(time.time())}",
                        'time': datetime.now().isoformat(),
                        'symbol': symbol, 
                        'side': side, 
                        'amount': amount, 
                        'price': exec_price, 
                        'cost': cost,
                        'type': 'entry'
                    })
                    return {'status': 'closed', 'price': exec_price, 'id': f'mock_{int(time.time())}'}
                else:
                    return {'status': 'rejected', 'reason': 'Insufficent funds'}
                    
            elif side == 'sell':
                if self.simulated_balance.get(base, 0) >= amount:
                    self.simulated_balance[base] -= amount
                    self.simulated_balance[quote] = self.simulated_balance.get(quote, 0) + cost
                    self.pm.save_balance(self.simulated_balance)
                    self.pm.update_position(symbol, 'sell', amount, exec_price)
                    return {'status': 'closed', 'price': exec_price, 'id': f'mock_{int(time.time())}'}
                else:
                    return {'status': 'rejected', 'reason': 'Insufficent holdings'}

        # --- TESTNET / LIVE MODE ---
        else:
            print(f"[{self.mode.upper()}] Sending Order: {side} {amount} {symbol}")
            
            if self.mode == 'live':
                # EXTRA SAFETY CHECK
                confirm = input(f"WARNING: Placing LIVE order for {amount} {symbol}. Type 'YES' to confirm: ")
                if confirm != 'YES':
                    print("Order Cancelled by User Safety Check.")
                    return {'status': 'cancelled'}

            try:
                # Basic Market Order
                order = self.exchange.create_order(
                    symbol=symbol,
                    type=order_type,
                    side=side,
                    amount=amount,
                    price=price
                )
                
                # TODO: If SL/TP provided, place OCO or conditional orders (Complex, skipped for MVP)
                if sl or tp:
                    print(f"Warning: SL/TP ({sl}/{tp}) not yet supported in {self.mode} mode via simple API.")
                    
                return order
            except Exception as e:
                print(f"Order placement failed: {e}")
                return {'status': 'failed', 'error': str(e)}
