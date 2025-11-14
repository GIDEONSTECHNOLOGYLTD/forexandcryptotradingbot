"""
Risk Management Module
Handles position sizing, stop-loss, take-profit, and risk controls
"""
import config
from datetime import datetime, timedelta


class RiskManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_pnl = 0
        self.daily_reset_time = datetime.now().date()
        self.open_positions = {}
        self.trade_history = []
        
    def reset_daily_stats(self):
        """Reset daily statistics"""
        current_date = datetime.now().date()
        if current_date > self.daily_reset_time:
            self.daily_pnl = 0
            self.daily_reset_time = current_date
            
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
        
        return trade_record
    
    def check_stop_loss_take_profit(self, symbol, current_price):
        """
        Check if stop loss or take profit has been hit
        Returns: 'stop_loss', 'take_profit', or None
        """
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        
        if position['side'] == 'long':
            if current_price <= position['stop_loss']:
                return 'stop_loss'
            elif current_price >= position['take_profit']:
                return 'take_profit'
        else:  # short
            if current_price >= position['stop_loss']:
                return 'stop_loss'
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
