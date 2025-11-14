"""
Advanced Risk Management System
Dynamic position sizing, portfolio optimization, and advanced risk controls
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.optimize import minimize
import config


class AdvancedRiskManager:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.daily_pnl = 0
        self.daily_reset_time = datetime.now().date()
        self.open_positions = {}
        self.trade_history = []
        self.correlation_matrix = {}
        self.volatility_estimates = {}
        self.drawdown_tracker = []
        self.max_drawdown = 0
        
    def calculate_dynamic_position_size(self, symbol, entry_price, confidence, volatility, correlation_risk=1.0):
        """
        Calculate position size using advanced portfolio theory
        Incorporates Kelly Criterion, volatility adjustment, and correlation risk
        """
        # Base Kelly Criterion calculation
        win_rate = self._estimate_win_rate(symbol, confidence)
        avg_win_loss_ratio = self._estimate_win_loss_ratio(symbol)
        
        # Kelly fraction: f = (bp - q) / b
        # where b = avg_win/avg_loss, p = win_rate, q = 1-win_rate
        if avg_win_loss_ratio > 0:
            kelly_fraction = (avg_win_loss_ratio * win_rate - (1 - win_rate)) / avg_win_loss_ratio
        else:
            kelly_fraction = 0.02  # Conservative fallback
        
        # Cap Kelly fraction to prevent over-leverage
        kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Max 25% of capital
        
        # Adjust for confidence
        confidence_multiplier = confidence / 100
        adjusted_kelly = kelly_fraction * confidence_multiplier
        
        # Volatility adjustment
        volatility_adjustment = self._calculate_volatility_adjustment(volatility)
        
        # Correlation risk adjustment
        correlation_adjustment = 1 / correlation_risk
        
        # Final position size calculation
        risk_per_trade = adjusted_kelly * volatility_adjustment * correlation_adjustment
        
        # Apply maximum position size limits
        max_position_percent = config.MAX_POSITION_SIZE_PERCENT / 100
        risk_per_trade = min(risk_per_trade, max_position_percent)
        
        # Calculate actual position size
        position_value = self.current_capital * risk_per_trade
        position_size = position_value / entry_price
        
        return position_size, risk_per_trade
    
    def _estimate_win_rate(self, symbol, confidence):
        """Estimate win rate based on historical performance and confidence"""
        # Get historical trades for this symbol
        symbol_trades = [t for t in self.trade_history if t['symbol'] == symbol]
        
        if len(symbol_trades) >= 10:
            wins = sum(1 for t in symbol_trades if t['pnl'] > 0)
            historical_win_rate = wins / len(symbol_trades)
        else:
            # Use overall win rate if insufficient symbol-specific data
            if len(self.trade_history) >= 10:
                wins = sum(1 for t in self.trade_history if t['pnl'] > 0)
                historical_win_rate = wins / len(self.trade_history)
            else:
                historical_win_rate = 0.55  # Optimistic default
        
        # Adjust based on confidence
        confidence_factor = (confidence - 50) / 100  # -0.5 to 0.45
        adjusted_win_rate = historical_win_rate + (confidence_factor * 0.2)
        
        return max(0.1, min(0.9, adjusted_win_rate))
    
    def _estimate_win_loss_ratio(self, symbol):
        """Estimate average win to average loss ratio"""
        symbol_trades = [t for t in self.trade_history if t['symbol'] == symbol]
        
        if len(symbol_trades) < 5:
            symbol_trades = self.trade_history  # Use all trades if insufficient data
        
        if len(symbol_trades) < 5:
            return 1.5  # Default assumption of 1.5:1 win/loss ratio
        
        wins = [t['pnl'] for t in symbol_trades if t['pnl'] > 0]
        losses = [abs(t['pnl']) for t in symbol_trades if t['pnl'] <= 0]
        
        if not wins or not losses:
            return 1.5
        
        avg_win = np.mean(wins)
        avg_loss = np.mean(losses)
        
        return avg_win / avg_loss if avg_loss > 0 else 1.5
    
    def _calculate_volatility_adjustment(self, volatility):
        """Adjust position size based on volatility"""
        # Higher volatility = smaller position
        if volatility > 0.05:  # High volatility (>5%)
            return 0.5
        elif volatility > 0.03:  # Medium volatility (3-5%)
            return 0.75
        elif volatility > 0.01:  # Low volatility (1-3%)
            return 1.0
        else:  # Very low volatility (<1%)
            return 1.25
    
    def calculate_portfolio_correlation_risk(self, new_symbol, existing_positions):
        """Calculate correlation risk when adding new position"""
        if not existing_positions:
            return 1.0
        
        # Simplified correlation calculation
        # In production, use actual price correlation data
        correlation_penalty = 1.0
        
        for existing_symbol in existing_positions:
            # Estimate correlation based on asset class
            correlation = self._estimate_correlation(new_symbol, existing_symbol)
            if correlation > 0.7:  # High correlation
                correlation_penalty += 0.5
            elif correlation > 0.5:  # Medium correlation
                correlation_penalty += 0.3
            elif correlation > 0.3:  # Low correlation
                correlation_penalty += 0.1
        
        return correlation_penalty
    
    def _estimate_correlation(self, symbol1, symbol2):
        """Estimate correlation between two symbols"""
        # Simplified correlation estimation
        # In production, calculate from actual price data
        
        base1 = symbol1.split('/')[0]
        base2 = symbol2.split('/')[0]
        
        # Same base currency = high correlation
        if base1 == base2:
            return 0.95
        
        # Major cryptos tend to be correlated
        major_cryptos = ['BTC', 'ETH', 'BNB', 'ADA', 'SOL', 'DOT']
        if base1 in major_cryptos and base2 in major_cryptos:
            return 0.75
        
        # Different asset classes = lower correlation
        return 0.3
    
    def calculate_dynamic_stop_loss(self, entry_price, volatility, confidence, side='long'):
        """Calculate dynamic stop loss based on volatility and confidence"""
        # Base stop loss from config
        base_stop_percent = config.STOP_LOSS_PERCENT / 100
        
        # Adjust based on volatility (higher volatility = wider stops)
        volatility_multiplier = 1 + (volatility * 10)  # Scale volatility
        
        # Adjust based on confidence (higher confidence = tighter stops)
        confidence_multiplier = 1 - ((confidence - 50) / 200)  # 0.75 to 1.25
        
        # Calculate dynamic stop loss percentage
        dynamic_stop_percent = base_stop_percent * volatility_multiplier * confidence_multiplier
        
        # Cap the stop loss
        dynamic_stop_percent = max(0.01, min(dynamic_stop_percent, 0.1))  # 1% to 10%
        
        # Normalize side to 'long' or 'short'
        normalized_side = 'long' if side.lower() in ['long', 'buy'] else 'short'
        
        if normalized_side == 'long':
            stop_loss = entry_price * (1 - dynamic_stop_percent)
        else:  # short
            stop_loss = entry_price * (1 + dynamic_stop_percent)
        
        return stop_loss, dynamic_stop_percent
    
    def calculate_dynamic_take_profit(self, entry_price, volatility, confidence, side='long'):
        """Calculate dynamic take profit based on market conditions"""
        # Base take profit from config
        base_tp_percent = config.TAKE_PROFIT_PERCENT / 100
        
        # Adjust based on volatility (higher volatility = wider targets)
        volatility_multiplier = 1 + (volatility * 15)
        
        # Adjust based on confidence (higher confidence = wider targets)
        confidence_multiplier = 0.5 + (confidence / 100)  # 0.5 to 1.5
        
        # Calculate dynamic take profit percentage
        dynamic_tp_percent = base_tp_percent * volatility_multiplier * confidence_multiplier
        
        # Cap the take profit
        dynamic_tp_percent = max(0.02, min(dynamic_tp_percent, 0.5))  # 2% to 50%
        
        # Normalize side to 'long' or 'short'
        normalized_side = 'long' if side.lower() in ['long', 'buy'] else 'short'
        
        if normalized_side == 'long':
            take_profit = entry_price * (1 + dynamic_tp_percent)
        else:  # short
            take_profit = entry_price * (1 - dynamic_tp_percent)
        
        return take_profit, dynamic_tp_percent
    
    def calculate_trailing_stop(self, symbol, current_price, highest_price_since_entry=None):
        """Calculate trailing stop loss"""
        if symbol not in self.open_positions:
            return None
        
        position = self.open_positions[symbol]
        entry_price = position['entry_price']
        side = position['side']
        
        # Calculate current profit
        if side == 'long':
            current_profit_percent = (current_price - entry_price) / entry_price
        else:
            current_profit_percent = (entry_price - current_price) / entry_price
        
        # Only activate trailing stop after minimum profit
        min_profit_for_trailing = 0.02  # 2%
        if current_profit_percent < min_profit_for_trailing:
            return position['stop_loss']  # Keep original stop loss
        
        # Calculate trailing stop distance (percentage of current profit to preserve)
        trailing_percent = 0.5  # Preserve 50% of current profit
        
        if side == 'long':
            if highest_price_since_entry:
                trailing_stop = highest_price_since_entry * (1 - trailing_percent * current_profit_percent)
            else:
                trailing_stop = current_price * (1 - trailing_percent * current_profit_percent)
        else:
            if highest_price_since_entry:
                trailing_stop = highest_price_since_entry * (1 + trailing_percent * current_profit_percent)
            else:
                trailing_stop = current_price * (1 + trailing_percent * current_profit_percent)
        
        # Ensure trailing stop is better than original stop loss
        if side == 'long':
            return max(trailing_stop, position['stop_loss'])
        else:
            return min(trailing_stop, position['stop_loss'])
    
    def check_portfolio_risk_limits(self):
        """Check overall portfolio risk limits"""
        # Calculate current drawdown
        current_drawdown = self._calculate_current_drawdown()
        
        # Check maximum drawdown limit
        max_allowed_drawdown = 0.15  # 15%
        if current_drawdown > max_allowed_drawdown:
            return False, f"Maximum drawdown exceeded: {current_drawdown:.2%}"
        
        # Check correlation risk
        correlation_risk = self._calculate_portfolio_correlation_risk()
        max_correlation_risk = 3.0
        if correlation_risk > max_correlation_risk:
            return False, f"Portfolio correlation risk too high: {correlation_risk:.2f}"
        
        # Check position concentration
        max_single_position = 0.3  # 30% of portfolio
        for position in self.open_positions.values():
            position_percent = (position['position_value'] / self.current_capital)
            if position_percent > max_single_position:
                return False, f"Single position too large: {position_percent:.2%}"
        
        return True, "Portfolio risk within limits"
    
    def _calculate_current_drawdown(self):
        """Calculate current portfolio drawdown"""
        if not self.drawdown_tracker:
            return 0
        
        peak_capital = max(self.drawdown_tracker)
        current_drawdown = (peak_capital - self.current_capital) / peak_capital
        return max(0, current_drawdown)
    
    def _calculate_portfolio_correlation_risk(self):
        """Calculate overall portfolio correlation risk"""
        if len(self.open_positions) <= 1:
            return 1.0
        
        symbols = list(self.open_positions.keys())
        total_correlation = 0
        pairs = 0
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                correlation = self._estimate_correlation(symbols[i], symbols[j])
                total_correlation += correlation
                pairs += 1
        
        return 1 + (total_correlation / pairs) if pairs > 0 else 1.0
    
    def optimize_portfolio_allocation(self):
        """Optimize portfolio allocation using modern portfolio theory"""
        if len(self.open_positions) < 2:
            return {}
        
        # This is a simplified version
        # In production, implement full Markowitz optimization
        symbols = list(self.open_positions.keys())
        n_assets = len(symbols)
        
        # Equal weight as starting point
        equal_weight = 1.0 / n_assets
        target_allocations = {symbol: equal_weight for symbol in symbols}
        
        # Adjust based on performance and correlation
        for symbol in symbols:
            position = self.open_positions[symbol]
            
            # Increase allocation for profitable positions
            if 'unrealized_pnl' in position and position['unrealized_pnl'] > 0:
                target_allocations[symbol] *= 1.1
            
            # Decrease allocation for correlated positions
            correlation_penalty = self.calculate_portfolio_correlation_risk(symbol, 
                                                                          [s for s in symbols if s != symbol])
            target_allocations[symbol] /= correlation_penalty
        
        # Normalize allocations
        total_allocation = sum(target_allocations.values())
        target_allocations = {k: v / total_allocation for k, v in target_allocations.items()}
        
        return target_allocations
    
    def update_position_tracking(self, symbol, current_price):
        """Update position tracking with current market data"""
        if symbol not in self.open_positions:
            return
        
        position = self.open_positions[symbol]
        
        # Update unrealized PnL
        if position['side'] == 'long':
            unrealized_pnl = (current_price - position['entry_price']) * position['amount']
        else:
            unrealized_pnl = (position['entry_price'] - current_price) * position['amount']
        
        position['unrealized_pnl'] = unrealized_pnl
        position['current_price'] = current_price
        position['last_update'] = datetime.now()
        
        # Update trailing stop if applicable
        if 'use_trailing_stop' in position and position['use_trailing_stop']:
            if 'highest_price' not in position:
                position['highest_price'] = current_price
            
            if position['side'] == 'long' and current_price > position['highest_price']:
                position['highest_price'] = current_price
            elif position['side'] == 'short' and current_price < position['highest_price']:
                position['highest_price'] = current_price
            
            # Update trailing stop
            new_stop = self.calculate_trailing_stop(symbol, current_price, position['highest_price'])
            if new_stop:
                position['stop_loss'] = new_stop
    
    def get_advanced_statistics(self):
        """Get comprehensive risk and performance statistics"""
        basic_stats = self.get_basic_statistics()
        
        # Advanced metrics
        advanced_stats = {
            **basic_stats,
            'max_drawdown': self._calculate_max_drawdown(),
            'current_drawdown': self._calculate_current_drawdown(),
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'sortino_ratio': self._calculate_sortino_ratio(),
            'calmar_ratio': self._calculate_calmar_ratio(),
            'portfolio_correlation_risk': self._calculate_portfolio_correlation_risk(),
            'var_95': self._calculate_var(0.95),
            'expected_shortfall': self._calculate_expected_shortfall(),
            'kelly_fraction': self._calculate_optimal_kelly(),
            'risk_adjusted_return': self._calculate_risk_adjusted_return()
        }
        
        return advanced_stats
    
    def _calculate_max_drawdown(self):
        """Calculate maximum historical drawdown"""
        if len(self.drawdown_tracker) < 2:
            return 0
        
        peak = self.drawdown_tracker[0]
        max_dd = 0
        
        for value in self.drawdown_tracker:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def _calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """Calculate Sharpe ratio"""
        if len(self.trade_history) < 10:
            return 0
        
        returns = [t['pnl_percent'] / 100 for t in self.trade_history]
        excess_returns = [r - risk_free_rate / 252 for r in returns]  # Daily risk-free rate
        
        if np.std(excess_returns) == 0:
            return 0
        
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)  # Annualized
    
    def _calculate_sortino_ratio(self, risk_free_rate=0.02):
        """Calculate Sortino ratio (downside deviation)"""
        if len(self.trade_history) < 10:
            return 0
        
        returns = [t['pnl_percent'] / 100 for t in self.trade_history]
        excess_returns = [r - risk_free_rate / 252 for r in returns]
        
        negative_returns = [r for r in excess_returns if r < 0]
        if not negative_returns:
            return float('inf')
        
        downside_deviation = np.std(negative_returns)
        if downside_deviation == 0:
            return 0
        
        return np.mean(excess_returns) / downside_deviation * np.sqrt(252)
    
    def _calculate_calmar_ratio(self):
        """Calculate Calmar ratio (return/max drawdown)"""
        max_dd = self._calculate_max_drawdown()
        if max_dd == 0:
            return float('inf')
        
        annual_return = ((self.current_capital / self.initial_capital) ** (252 / len(self.trade_history))) - 1
        return annual_return / max_dd
    
    def _calculate_var(self, confidence_level):
        """Calculate Value at Risk"""
        if len(self.trade_history) < 10:
            return 0
        
        returns = [t['pnl_percent'] / 100 for t in self.trade_history]
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def _calculate_expected_shortfall(self, confidence_level=0.95):
        """Calculate Expected Shortfall (Conditional VaR)"""
        var = self._calculate_var(confidence_level)
        returns = [t['pnl_percent'] / 100 for t in self.trade_history]
        tail_returns = [r for r in returns if r <= var]
        
        return np.mean(tail_returns) if tail_returns else 0
    
    def _calculate_optimal_kelly(self):
        """Calculate optimal Kelly fraction based on historical performance"""
        if len(self.trade_history) < 20:
            return 0.02
        
        win_rate = self._estimate_win_rate('overall', 70)
        win_loss_ratio = self._estimate_win_loss_ratio('overall')
        
        kelly = (win_loss_ratio * win_rate - (1 - win_rate)) / win_loss_ratio
        return max(0, min(kelly, 0.25))  # Cap at 25%
    
    def _calculate_risk_adjusted_return(self):
        """Calculate risk-adjusted return"""
        total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        max_dd = self._calculate_max_drawdown()
        
        if max_dd == 0:
            return total_return
        
        return total_return / max_dd
    
    def get_basic_statistics(self):
        """Get basic trading statistics (compatibility with existing code)"""
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
        
        return {
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
