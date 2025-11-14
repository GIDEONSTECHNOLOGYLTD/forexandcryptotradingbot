"""
Enhanced Risk Management
Kelly Criterion + Dynamic Risk Management
Optimal position sizing for maximum growth
"""

import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EnhancedRiskManager:
    """
    Enhanced Risk Manager with Kelly Criterion
    Calculates optimal position sizes
    Adjusts stops/targets based on volatility
    """
    
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trade_history = []
        self.open_positions = {}
        self.max_positions = 3
        self.daily_pnl = 0
        self.daily_loss_limit = initial_capital * 0.10  # 10% daily loss limit
        logger.info(f"Enhanced Risk Manager initialized: ${initial_capital}")
    
    def kelly_criterion_position_size(self):
        """
        Calculate optimal position size using Kelly Criterion
        f* = (p*b - q) / b
        where:
        f* = fraction of capital to bet
        p = probability of winning (win rate)
        b = win/loss ratio (avg_win / avg_loss)
        q = probability of losing (1-p)
        """
        if len(self.trade_history) < 20:
            # Not enough data, use conservative 10%
            logger.info("Not enough trades for Kelly, using 10% default")
            return 0.10
        
        wins = [t for t in self.trade_history if t['pnl'] > 0]
        losses = [t for t in self.trade_history if t['pnl'] < 0]
        
        if not wins or not losses:
            return 0.10
        
        # Calculate probabilities
        win_rate = len(wins) / len(self.trade_history)
        loss_rate = 1 - win_rate
        
        # Calculate average win/loss
        avg_win = np.mean([t['pnl'] for t in wins])
        avg_loss = abs(np.mean([t['pnl'] for t in losses]))
        
        if avg_loss == 0:
            return 0.10
        
        win_loss_ratio = avg_win / avg_loss
        
        # Kelly formula
        kelly = (win_rate * win_loss_ratio - loss_rate) / win_loss_ratio
        
        # Use half Kelly (safer)
        position_size = kelly * 0.5
        
        # Cap at 25% maximum, minimum 5%
        position_size = max(min(position_size, 0.25), 0.05)
        
        logger.info(f"Kelly Criterion: {position_size*100:.1f}% (Win rate: {win_rate*100:.1f}%, W/L ratio: {win_loss_ratio:.2f})")
        
        return position_size
    
    def calculate_position_amount(self, symbol, price):
        """
        Calculate optimal position amount
        """
        kelly_fraction = self.kelly_criterion_position_size()
        
        # Adjust for current drawdown
        if self.should_reduce_risk():
            kelly_fraction *= 0.5  # Halve position size during drawdown
            logger.info("Reducing position size due to drawdown")
        
        # Calculate amount
        position_value = self.current_capital * kelly_fraction
        amount = position_value / price
        
        return amount
    
    def dynamic_stop_loss(self, symbol, volatility):
        """
        Adjust stop loss based on market volatility
        TIGHTENED FOR USER PROTECTION!
        """
        base_stop = 0.03  # 3% base (tightened from 2%)
        
        if volatility > 0.05:  # High volatility (5%+)
            stop_loss = 0.05  # 5% stop (MAXIMUM ALLOWED!)
            logger.info(f"{symbol}: High volatility, using 5% stop")
        elif volatility > 0.03:  # Medium volatility (3-5%)
            stop_loss = 0.04  # 4% stop (tightened from 3%)
            logger.info(f"{symbol}: Medium volatility, using 4% stop")
        else:  # Low volatility (<3%)
            stop_loss = base_stop  # 3% stop (tightened from 2%)
            logger.info(f"{symbol}: Low volatility, using 3% stop")
        
        return stop_loss
    
    def dynamic_take_profit(self, symbol, volatility, trend_strength):
        """
        Adjust take profit based on market conditions
        Strong trend = let it run
        High volatility = take profit faster
        """
        base_tp = 0.04  # 4% base
        
        # Strong trend = let it run
        if trend_strength > 0.7:
            take_profit = base_tp * 2  # 8% take profit
            logger.info(f"{symbol}: Strong trend, using 8% take profit")
        
        # Volatile market = take profit faster
        elif volatility > 0.05:
            take_profit = base_tp * 0.75  # 3% take profit
            logger.info(f"{symbol}: High volatility, using 3% take profit")
        
        else:
            take_profit = base_tp  # 4% take profit
        
        return take_profit
    
    def calculate_atr(self, df, period=14):
        """
        Calculate Average True Range (volatility measure)
        """
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean().iloc[-1]
        
        return atr
    
    def should_reduce_risk(self):
        """
        Check if we should reduce position sizes due to drawdown
        """
        if len(self.trade_history) < 10:
            return False
        
        # Check last 10 trades
        recent = self.trade_history[-10:]
        recent_pnl = sum(t['pnl'] for t in recent)
        
        # If down more than 10% in last 10 trades
        if recent_pnl < -self.initial_capital * 0.10:
            logger.warning(f"Drawdown detected: ${recent_pnl:.2f} in last 10 trades")
            return True
        
        return False
    
    def can_open_position(self, symbol, amount, price):
        """
        Check if we can open a new position
        """
        # Check 1: Max positions limit
        if len(self.open_positions) >= self.max_positions:
            return False, f"Max positions reached ({self.max_positions})"
        
        # Check 2: Already have this position
        if symbol in self.open_positions:
            return False, f"Position already open for {symbol}"
        
        # Check 3: Enough capital
        required_capital = amount * price
        if required_capital > self.current_capital:
            return False, "Insufficient capital"
        
        # Check 4: Daily loss limit
        if self.daily_pnl < -self.daily_loss_limit:
            return False, f"Daily loss limit reached (${self.daily_loss_limit:.2f})"
        
        # All checks passed
        return True, "OK"
    
    def add_position(self, symbol, amount, entry_price, stop_loss_percent, take_profit_percent):
        """
        Add a new position
        """
        self.open_positions[symbol] = {
            'symbol': symbol,
            'amount': amount,
            'entry_price': entry_price,
            'stop_loss': entry_price * (1 - stop_loss_percent),
            'take_profit': entry_price * (1 + take_profit_percent),
            'stop_loss_percent': stop_loss_percent,
            'take_profit_percent': take_profit_percent,
            'opened_at': datetime.utcnow()
        }
        
        # Update capital
        self.current_capital -= amount * entry_price
        
        logger.info(f"Position opened: {symbol} @ ${entry_price:.2f}, SL: ${self.open_positions[symbol]['stop_loss']:.2f}, TP: ${self.open_positions[symbol]['take_profit']:.2f}")
    
    def check_exit_conditions(self, symbol, current_price):
        """
        Check if position should be closed
        """
        if symbol not in self.open_positions:
            return None, None
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        
        # Calculate P&L
        pnl_percent = (current_price - entry_price) / entry_price
        pnl_amount = (current_price - entry_price) * position['amount']
        
        # Check stop loss
        if current_price <= position['stop_loss']:
            logger.info(f"Stop loss hit for {symbol}: ${current_price:.2f} <= ${position['stop_loss']:.2f}")
            return 'STOP_LOSS', pnl_amount
        
        # Check take profit
        if current_price >= position['take_profit']:
            logger.info(f"Take profit hit for {symbol}: ${current_price:.2f} >= ${position['take_profit']:.2f}")
            return 'TAKE_PROFIT', pnl_amount
        
        # Check time-based exit (24 hours)
        time_open = (datetime.utcnow() - position['opened_at']).total_seconds()
        if time_open > 86400:  # 24 hours
            logger.info(f"Time exit for {symbol}: {time_open/3600:.1f} hours open")
            return 'TIME_EXIT', pnl_amount
        
        return None, None
    
    def close_position(self, symbol, exit_price, exit_reason):
        """
        Close a position
        """
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        
        # Calculate P&L
        pnl = (exit_price - position['entry_price']) * position['amount']
        
        # Update capital
        self.current_capital += position['amount'] * exit_price
        
        # Update daily P&L
        self.daily_pnl += pnl
        
        # Record trade
        trade_record = {
            'symbol': symbol,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'amount': position['amount'],
            'pnl': pnl,
            'pnl_percent': (exit_price - position['entry_price']) / position['entry_price'] * 100,
            'exit_reason': exit_reason,
            'hold_time': (datetime.utcnow() - position['opened_at']).total_seconds(),
            'timestamp': datetime.utcnow()
        }
        
        self.trade_history.append(trade_record)
        
        # Remove position
        del self.open_positions[symbol]
        
        logger.info(f"Position closed: {symbol} @ ${exit_price:.2f}, P&L: ${pnl:.2f} ({trade_record['pnl_percent']:.2f}%), Reason: {exit_reason}")
        
        return trade_record
    
    def get_statistics(self):
        """
        Get trading statistics
        """
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
                'open_positions': len(self.open_positions),
                'kelly_size': self.kelly_criterion_position_size() * 100
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
            'open_positions': len(self.open_positions),
            'kelly_size': self.kelly_criterion_position_size() * 100
        }
        
        return stats
    
    def reset_daily_pnl(self):
        """
        Reset daily P&L (call at start of each day)
        """
        self.daily_pnl = 0
        logger.info("Daily P&L reset")
