"""
Smart Risk Manager with Dynamic Position Sizing and Portfolio Protection
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SmartRiskManager:
    """
    Advanced risk management with dynamic position sizing,
    correlation analysis, and portfolio-level risk controls
    """
    
    def __init__(self, initial_capital, max_risk_per_trade=0.02, max_portfolio_risk=0.06):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.max_risk_per_trade = max_risk_per_trade  # 2% per trade
        self.max_portfolio_risk = max_portfolio_risk  # 6% total portfolio risk
        self.max_drawdown_limit = 0.20  # 20% max drawdown
        
        self.open_positions = {}
        self.trade_history = []
        self.daily_pnl = 0
        self.peak_capital = initial_capital
        self.current_drawdown = 0
        
        # Risk metrics
        self.var_95 = 0  # Value at Risk (95% confidence)
        self.sharpe_ratio = 0
        self.sortino_ratio = 0
        
    def calculate_position_size(self, symbol, entry_price, stop_loss, confidence, volatility):
        """
        Calculate optimal position size using multiple factors:
        - Kelly Criterion
        - Volatility adjustment
        - Confidence level
        - Portfolio correlation
        """
        # Base risk amount
        risk_amount = self.current_capital * self.max_risk_per_trade
        
        # Adjust for confidence (higher confidence = larger position)
        confidence_multiplier = confidence / 100
        adjusted_risk = risk_amount * confidence_multiplier
        
        # Volatility adjustment (higher volatility = smaller position)
        volatility_adjustment = 1 / (1 + volatility)
        adjusted_risk *= volatility_adjustment
        
        # Calculate position size based on stop loss
        risk_per_unit = abs(entry_price - stop_loss)
        if risk_per_unit > 0:
            position_size = adjusted_risk / risk_per_unit
        else:
            position_size = 0
        
        # Apply maximum position size limit (20% of capital)
        max_position_value = self.current_capital * 0.20
        max_position_size = max_position_value / entry_price
        position_size = min(position_size, max_position_size)
        
        # Check portfolio-level risk
        if not self.check_portfolio_risk_limit(position_size, entry_price):
            position_size *= 0.5  # Reduce size if portfolio risk too high
        
        return position_size
    
    def check_portfolio_risk_limit(self, new_position_size, entry_price):
        """Check if adding new position exceeds portfolio risk limit"""
        # Calculate current portfolio risk
        current_risk = sum(pos['risk_amount'] for pos in self.open_positions.values())
        
        # Estimate new position risk (assuming 2% stop loss)
        new_risk = new_position_size * entry_price * 0.02
        
        total_risk = current_risk + new_risk
        risk_percentage = total_risk / self.current_capital
        
        return risk_percentage <= self.max_portfolio_risk
    
    def should_take_trade(self, symbol, confidence, market_conditions):
        """
        Determine if trade should be taken based on multiple factors
        """
        # Check if max positions reached
        if len(self.open_positions) >= 5:
            logger.warning("Maximum positions reached")
            return False
        
        # Check drawdown limit
        if self.current_drawdown >= self.max_drawdown_limit:
            logger.warning(f"Drawdown limit reached: {self.current_drawdown:.2%}")
            return False
        
        # Check daily loss limit (5% of capital)
        if self.daily_pnl < -(self.current_capital * 0.05):
            logger.warning("Daily loss limit reached")
            return False
        
        # Confidence threshold
        if confidence < 60:
            logger.info(f"Confidence too low: {confidence}")
            return False
        
        # Check if already have position in this symbol
        if symbol in self.open_positions:
            logger.info(f"Already have position in {symbol}")
            return False
        
        # Market conditions check
        if market_conditions.get('volatility', 0) > 0.05:  # 5% volatility threshold
            logger.warning("Market too volatile")
            return False
        
        return True
    
    def calculate_stop_loss(self, entry_price, signal, atr, support_resistance=None):
        """
        Calculate dynamic stop loss based on:
        - ATR (Average True Range)
        - Support/Resistance levels
        - Volatility
        """
        # ATR-based stop loss
        atr_multiplier = 1.5  # TIGHTENED: 1.5x ATR (was 2.0x) for tighter stops
        atr_stop = entry_price - (atr * atr_multiplier) if signal == 'buy' else entry_price + (atr * atr_multiplier)
        
        # Percentage-based stop loss (1% - TIGHTENED from 2%)
        pct_stop = entry_price * 0.99 if signal == 'buy' else entry_price * 1.01
        
        # Use support/resistance if available
        if support_resistance:
            if signal == 'buy':
                sr_stop = support_resistance.get('support', pct_stop)
                stop_loss = max(sr_stop, pct_stop)  # Don't go below percentage stop
            else:
                sr_stop = support_resistance.get('resistance', pct_stop)
                stop_loss = min(sr_stop, pct_stop)  # Don't go above percentage stop
        else:
            # Use the tighter of ATR or percentage stop
            if signal == 'buy':
                stop_loss = max(atr_stop, pct_stop)
            else:
                stop_loss = min(atr_stop, pct_stop)
        
        return stop_loss
    
    def calculate_take_profit(self, entry_price, stop_loss, signal, risk_reward_ratio=2.0):
        """Calculate take profit level based on risk-reward ratio"""
        risk = abs(entry_price - stop_loss)
        reward = risk * risk_reward_ratio
        
        if signal == 'buy':
            take_profit = entry_price + reward
        else:
            take_profit = entry_price - reward
        
        return take_profit
    
    def add_position(self, symbol, signal, entry_price, position_size, stop_loss, take_profit):
        """Add new position to portfolio"""
        risk_amount = abs(entry_price - stop_loss) * position_size
        
        self.open_positions[symbol] = {
            'signal': signal,
            'entry_price': entry_price,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_amount': risk_amount,
            'entry_time': datetime.now(),
            'current_price': entry_price,
            'unrealized_pnl': 0
        }
        
        logger.info(f"Position added: {symbol} {signal} @ {entry_price}")
    
    def update_position(self, symbol, current_price):
        """Update position with current price and P&L"""
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        position['current_price'] = current_price
        
        # Calculate unrealized P&L
        if position['signal'] == 'buy':
            pnl = (current_price - position['entry_price']) * position['position_size']
        else:
            pnl = (position['entry_price'] - current_price) * position['position_size']
        
        position['unrealized_pnl'] = pnl
        
        # Check for trailing stop
        self.update_trailing_stop(symbol, current_price)
    
    def update_trailing_stop(self, symbol, current_price):
        """Update trailing stop loss to lock in profits"""
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        
        # Only trail if in profit - TIGHTENED activation threshold
        if position['signal'] == 'buy':
            profit_pct = (current_price - entry_price) / entry_price
            if profit_pct > 0.005:  # 0.5% profit (was 3%) - trail much sooner!
                # Trail stop to 0.5% below current price (tighter protection)
                new_stop = current_price * 0.995
                position['stop_loss'] = max(position['stop_loss'], new_stop)
                logger.info(f"🛡️ Trailing stop updated for {symbol}: ${position['stop_loss']:.4f}")
        else:
            profit_pct = (entry_price - current_price) / entry_price
            if profit_pct > 0.005:
                new_stop = current_price * 1.005
                position['stop_loss'] = min(position['stop_loss'], new_stop)
                logger.info(f"🛡️ Trailing stop updated for {symbol}: ${position['stop_loss']:.4f}")
    
    def check_exit_conditions(self, symbol, current_price):
        """Check if position should be closed - includes multiple profit-taking levels"""
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        
        # Calculate current profit percentage
        if position['signal'] == 'buy':
            profit_pct = ((current_price - entry_price) / entry_price) * 100
            
            # Check stop loss first
            if current_price <= position['stop_loss']:
                return 'stop_loss'
            
            # MULTIPLE PROFIT-TAKING LEVELS - Take profits early!
            # Level 1: 1% profit (quick wins)
            elif profit_pct >= 1.0 and not position.get('took_profit_1'):
                position['took_profit_1'] = True
                return 'partial_profit_1'  # Take 30% of position
            
            # Level 2: 2% profit (good gains)
            elif profit_pct >= 2.0 and not position.get('took_profit_2'):
                position['took_profit_2'] = True
                return 'partial_profit_2'  # Take another 30% of remaining
            
            # Level 3: 3% profit (excellent gains)
            elif profit_pct >= 3.0:
                return 'take_profit_3'  # Close entire position
            
            # Full take profit target
            elif current_price >= position['take_profit']:
                return 'take_profit'
        else:
            profit_pct = ((entry_price - current_price) / entry_price) * 100
            
            if current_price >= position['stop_loss']:
                return 'stop_loss'
            
            # MULTIPLE PROFIT-TAKING LEVELS for short positions
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
        
        # Check time-based exit (close after 24 hours if no movement)
        time_in_position = datetime.now() - position['entry_time']
        if time_in_position > timedelta(hours=24):
            if abs(position['unrealized_pnl']) < position['risk_amount'] * 0.1:
                return 'time_exit'
        
        return None
    
    def close_position(self, symbol, exit_price, reason):
        """Close position and update capital"""
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        
        # Calculate realized P&L
        if position['signal'] == 'buy':
            pnl = (exit_price - position['entry_price']) * position['position_size']
        else:
            pnl = (position['entry_price'] - exit_price) * position['position_size']
        
        # Update capital
        self.current_capital += pnl
        self.daily_pnl += pnl
        
        # Update peak and drawdown
        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital
        
        self.current_drawdown = (self.peak_capital - self.current_capital) / self.peak_capital
        
        # Record trade
        trade_record = {
            'symbol': symbol,
            'signal': position['signal'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size': position['position_size'],
            'pnl': pnl,
            'pnl_pct': (pnl / (position['entry_price'] * position['position_size'])) * 100,
            'reason': reason,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'duration': datetime.now() - position['entry_time']
        }
        
        self.trade_history.append(trade_record)
        
        # Remove position
        del self.open_positions[symbol]
        
        logger.info(f"Position closed: {symbol} - P&L: ${pnl:.2f} ({reason})")
    
    def calculate_var(self, confidence=0.95):
        """Calculate Value at Risk"""
        if len(self.trade_history) < 30:
            return 0
        
        returns = [trade['pnl_pct'] for trade in self.trade_history[-30:]]
        var = np.percentile(returns, (1 - confidence) * 100)
        
        self.var_95 = var
        return var
    
    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """Calculate Sharpe Ratio"""
        if len(self.trade_history) < 30:
            return 0
        
        returns = [trade['pnl_pct'] for trade in self.trade_history[-30:]]
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return > 0:
            sharpe = (avg_return - risk_free_rate) / std_return
            self.sharpe_ratio = sharpe
            return sharpe
        
        return 0
    
    def get_risk_metrics(self):
        """Get comprehensive risk metrics"""
        total_trades = len(self.trade_history)
        
        if total_trades == 0:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'var_95': 0
            }
        
        winning_trades = [t for t in self.trade_history if t['pnl'] > 0]
        losing_trades = [t for t in self.trade_history if t['pnl'] <= 0]
        
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': (len(winning_trades) / total_trades) * 100,
            'avg_win': total_wins / len(winning_trades) if winning_trades else 0,
            'avg_loss': total_losses / len(losing_trades) if losing_trades else 0,
            'profit_factor': total_wins / total_losses if total_losses > 0 else float('inf'),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'max_drawdown': self.current_drawdown * 100,
            'var_95': self.calculate_var(),
            'current_capital': self.current_capital,
            'total_return': ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        }
    
    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of each day)"""
        self.daily_pnl = 0
