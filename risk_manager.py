"""
Risk Management Module
Handles position sizing, stop-loss, take-profit, and risk controls
"""
import config
import logging
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RiskManager:
    COOLDOWN_FILE = 'cooldown_data.json'
    
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_pnl = 0
        self.daily_reset_time = datetime.now().date()
        self.open_positions = {}
        self.trade_history = []
        self.recently_closed_positions = {}  # Track recently closed positions with cooldown
        
        # Load persisted cooldown data from previous session
        self._load_cooldown_data()
        
    def reset_daily_stats(self):
        """Reset daily statistics"""
        current_date = datetime.now().date()
        if current_date > self.daily_reset_time:
            self.daily_pnl = 0
            self.daily_reset_time = current_date
            
    def is_symbol_in_cooldown(self, symbol, cooldown_minutes=30):
        """
        Check if a symbol was recently closed and is in cooldown period
        Returns (is_in_cooldown, reason_message, expired_symbols_list)
        
        Also cleans up ANY expired cooldowns found, not just the one being checked.
        This prevents memory leaks when symbols leave active_symbols list.
        """
        # First, clean up ALL expired cooldowns (prevents memory leak)
        expired_symbols = []
        for sym in list(self.recently_closed_positions.keys()):
            close_time = self.recently_closed_positions[sym]['close_time']
            time_since_close = (datetime.now() - close_time).total_seconds() / 60
            
            if time_since_close >= cooldown_minutes:
                expired_symbols.append(sym)
                logger.info(f"Cooldown expired for {sym}, re-entry now allowed")
                del self.recently_closed_positions[sym]
        
        # Save if we cleaned up any expired cooldowns
        if expired_symbols:
            self._save_cooldown_data()
        
        # Now check the specific symbol requested
        if symbol in self.recently_closed_positions:
            close_time = self.recently_closed_positions[symbol]['close_time']
            pnl = self.recently_closed_positions[symbol]['pnl']
            time_since_close = (datetime.now() - close_time).total_seconds() / 60
            
            remaining_mins = int(cooldown_minutes - time_since_close)
            profit_status = "PROFIT" if pnl > 0 else "LOSS"
            return True, f"Symbol {symbol} recently closed with {profit_status} ${pnl:.2f}. Cooldown: {remaining_mins} mins remaining", expired_symbols
        
        return False, "", expired_symbols
    
    def get_recently_closed_symbols(self):
        """Get list of symbols currently in cooldown"""
        return list(self.recently_closed_positions.keys())
    
    def _load_cooldown_data(self, cooldown_minutes=30):
        """
        Load cooldown data from file (survives bot restarts)
        Automatically filters out expired cooldowns
        """
        try:
            if os.path.exists(self.COOLDOWN_FILE):
                with open(self.COOLDOWN_FILE, 'r') as f:
                    data = json.load(f)
                
                loaded_count = len(data)
                expired_count = 0
                
                # Convert timestamps and filter expired cooldowns
                for symbol, info in data.items():
                    info['close_time'] = datetime.fromisoformat(info['close_time'])
                    
                    # Check if cooldown is still valid
                    time_since_close = (datetime.now() - info['close_time']).total_seconds() / 60
                    
                    if time_since_close < cooldown_minutes:
                        # Still in cooldown, keep it
                        self.recently_closed_positions[symbol] = info
                    else:
                        # Expired, skip it
                        expired_count += 1
                        logger.info(f"Skipping expired cooldown for {symbol} (closed {time_since_close:.1f} mins ago)")
                
                logger.info(f"✅ Loaded cooldown data: {len(self.recently_closed_positions)} active, {expired_count} expired (filtered)")
                
                # Log which symbols are in cooldown
                for symbol in self.recently_closed_positions:
                    logger.info(f"  - {symbol}: {self.recently_closed_positions[symbol]}")
                
                # Save cleaned data back to file if we filtered any
                if expired_count > 0:
                    self._save_cooldown_data()
            else:
                logger.info("No previous cooldown data found (first run)")
        except Exception as e:
            logger.error(f"Error loading cooldown data: {e}")
            logger.error(f"Renaming corrupted file to {self.COOLDOWN_FILE}.corrupt")
            
            # Rename corrupted file so it doesn't cause issues on next load
            try:
                if os.path.exists(self.COOLDOWN_FILE):
                    os.rename(self.COOLDOWN_FILE, f"{self.COOLDOWN_FILE}.corrupt")
            except:
                pass
            
            self.recently_closed_positions = {}
    
    def _save_cooldown_data(self):
        """
        Save cooldown data to file (persists across restarts)
        Deletes file if empty to keep directory clean
        """
        try:
            # If no cooldowns, delete the file instead of saving empty data
            if not self.recently_closed_positions:
                if os.path.exists(self.COOLDOWN_FILE):
                    os.remove(self.COOLDOWN_FILE)
                    logger.info(f"✅ Deleted empty cooldown file (all cooldowns expired)")
                return
            
            # Convert datetime objects to ISO format strings for JSON
            data = {}
            for symbol, info in self.recently_closed_positions.items():
                data[symbol] = {
                    'close_time': info['close_time'].isoformat(),
                    'pnl': info['pnl'],
                    'exit_price': info['exit_price'],
                    'exit_reason': info['exit_reason']
                }
            
            with open(self.COOLDOWN_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"✅ Saved cooldown data: {len(data)} symbols")
        except Exception as e:
            logger.error(f"Error saving cooldown data: {e}")
    
    def can_trade(self):
        """Check if trading is allowed based on risk parameters"""
        self.reset_daily_stats()
        
        # Check daily loss limit
        daily_loss_percent = (self.daily_pnl / self.current_capital) * 100
        if daily_loss_percent <= -config.MAX_DAILY_LOSS_PERCENT:
            return False, f"Daily loss limit reached: {daily_loss_percent:.2f}%"
        
        # Check max open positions
        if len(self.open_positions) >= config.MAX_OPEN_POSITIONS:
            return False, f"Maximum open positions reached: {len(self.open_positions)}"
        
        return True, "Trading allowed"
    
    def calculate_position_size(self, symbol, entry_price):
        """
        Calculate position size based on risk management rules
        Returns the amount to trade
        """
        # Calculate max position value based on portfolio percentage
        max_position_value = self.current_capital * (config.MAX_POSITION_SIZE_PERCENT / 100)
        
        # Calculate position size
        position_size = max_position_value / entry_price
        
        return position_size
    
    def calculate_stop_loss(self, entry_price, side='long'):
        """Calculate stop loss price"""
        # Normalize side to 'long' or 'short'
        normalized_side = 'long' if side.lower() in ['long', 'buy'] else 'short'
        
        if normalized_side == 'long':
            stop_loss = entry_price * (1 - config.STOP_LOSS_PERCENT / 100)
        else:  # short
            stop_loss = entry_price * (1 + config.STOP_LOSS_PERCENT / 100)
        return stop_loss
    
    def calculate_take_profit(self, entry_price, side='long'):
        """Calculate take profit price"""
        # Normalize side to 'long' or 'short'
        normalized_side = 'long' if side.lower() in ['long', 'buy'] else 'short'
        
        if normalized_side == 'long':
            take_profit = entry_price * (1 + config.TAKE_PROFIT_PERCENT / 100)
        else:  # short
            take_profit = entry_price * (1 - config.TAKE_PROFIT_PERCENT / 100)
        return take_profit
    
    def open_position(self, symbol, side, entry_price, amount):
        """Record a new position"""
        position = {
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'amount': amount,
            'entry_time': datetime.now(),
            'stop_loss': self.calculate_stop_loss(entry_price, side),
            'take_profit': self.calculate_take_profit(entry_price, side),
            'position_value': entry_price * amount
        }
        
        # CRITICAL: Subtract position value from available capital
        position_value = entry_price * amount
        self.current_capital -= position_value
        logger.info(f"Position opened: {symbol}, Capital: ${self.current_capital:.2f} (used ${position_value:.2f})")
        
        self.open_positions[symbol] = position
        return position
    
    def close_position(self, symbol, exit_price):
        """Close a position and calculate PnL"""
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        
        # Calculate PnL
        if position['side'] == 'long' or position['side'] == 'buy':
            pnl = (exit_price - position['entry_price']) * position['amount']
        else:  # short or sell
            pnl = (position['entry_price'] - exit_price) * position['amount']
        
        pnl_percent = (pnl / position['position_value']) * 100 if position['position_value'] > 0 else 0
        
        # Update capital: Add back the exit value (not just PnL)
        exit_value = exit_price * position['amount']
        self.current_capital += exit_value
        self.daily_pnl += pnl
        logger.info(f"Position closed: {symbol}, Capital: ${self.current_capital:.2f} (returned ${exit_value:.2f}, PnL: ${pnl:.2f})")
        
        # Record trade
        trade_record = {
            **position,
            'exit_price': exit_price,
            'exit_time': datetime.now(),
            'pnl': pnl,
            'pnl_percent': pnl_percent,
            'duration': datetime.now() - position['entry_time']
        }
        
        self.trade_history.append(trade_record)
        
        # Remove from open positions
        del self.open_positions[symbol]
        
        # Add to recently closed positions for cooldown tracking
        self.recently_closed_positions[symbol] = {
            'close_time': datetime.now(),
            'pnl': pnl,
            'exit_price': exit_price,
            'exit_reason': trade_record.get('exit_reason', 'manual')
        }
        logger.info(f"Symbol {symbol} added to cooldown - PnL: ${pnl:.2f}")
        
        # Save cooldown data to persist across restarts
        self._save_cooldown_data()
        
        return trade_record
    
    def check_stop_loss_take_profit(self, symbol, current_price):
        """
        Check if stop loss or take profit has been hit
        Returns: 'stop_loss', 'take_profit', 'partial_profit_1/2/3', or None
        
        IMPORTANT NOTE: Despite the name "partial_profit", the bot closes 100% of the position
        when ANY of these profit levels are hit. The levels are tiered exit points:
        - 1% = Quick exit (capture small wins fast)
        - 2% = Good profit exit
        - 3% = Excellent profit exit
        
        This is a "SCALPING STRATEGY" - take profits early and often, rather than
        holding for bigger gains. The bot will only hit ONE of these levels before
        closing the entire position.
        
        If you want true partial exits (sell 25%, 50%, 75%), that requires different logic.
        """
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        
        if position['side'] == 'long' or position['side'] == 'buy':
            # Calculate profit percentage
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Check stop loss first
            if current_price <= position['stop_loss']:
                return 'stop_loss'
            
            # TIERED EXIT STRATEGY - First profit level hit = FULL EXIT
            # Level 1: 1% profit (quick scalp exit - closes 100%)
            elif profit_pct >= 1.0 and not position.get('took_profit_1'):
                position['took_profit_1'] = True
                return 'partial_profit_1'  # NOTE: Closes 100% despite name
            
            # Level 2: 2% profit (if 1% was missed - closes 100%)
            elif profit_pct >= 2.0 and not position.get('took_profit_2'):
                position['took_profit_2'] = True
                return 'partial_profit_2'  # NOTE: Closes 100% despite name
            
            # Level 3: 3% profit (if 1% and 2% were missed - closes 100%)
            elif profit_pct >= 3.0:
                return 'take_profit_3'  # Closes 100%
            
            # Full take profit target (from config)
            elif current_price >= position['take_profit']:
                return 'take_profit'
                
        else:  # short or sell
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            
            if current_price >= position['stop_loss']:
                return 'stop_loss'
            
            elif profit_pct >= 1.0 and not position.get('took_profit_1'):
                position['took_profit_1'] = True
                return 'partial_profit_1'
            
            elif profit_pct >= 2.0 and not position.get('took_profit_2'):
                position['took_profit_2'] = True
                return 'partial_profit_2'
            
            elif profit_pct >= 3.0:
                return 'take_profit_3'
            
            elif current_price <= position['take_profit']:
                return 'take_profit'
        
        return None
    
    def get_statistics(self):
        """Get trading statistics"""
        if not self.trade_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_pnl_percent': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'current_capital': self.current_capital,
                'daily_pnl': self.daily_pnl,
                'open_positions': len(self.open_positions)
            }
        
        winning_trades = [t for t in self.trade_history if t['pnl'] > 0]
        losing_trades = [t for t in self.trade_history if t['pnl'] <= 0]
        
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
        
        stats = {
            'total_trades': len(self.trade_history),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / len(self.trade_history)) * 100,
            'total_pnl': self.current_capital - self.initial_capital,
            'total_pnl_percent': ((self.current_capital - self.initial_capital) / self.initial_capital) * 100,
            'avg_win': total_wins / len(winning_trades) if winning_trades else 0,
            'avg_loss': total_losses / len(losing_trades) if losing_trades else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else float('inf'),
            'current_capital': self.current_capital,
            'daily_pnl': self.daily_pnl,
            'open_positions': len(self.open_positions)
        }
        
        return stats
