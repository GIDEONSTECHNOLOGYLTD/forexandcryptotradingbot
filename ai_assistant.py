"""
AI Trading Assistant
Analyzes user performance and provides personalized suggestions
Helps users improve their trading
"""

import numpy as np
from datetime import datetime, timedelta
import logging
from collections import Counter

logger = logging.getLogger(__name__)


class AITradingAssistant:
    """
    AI-powered trading assistant
    Analyzes performance and provides actionable suggestions
    """
    
    def __init__(self, db):
        self.db = db
        logger.info("AI Trading Assistant initialized")
    
    def analyze_user_performance(self, user_id):
        """
        Comprehensive analysis of user's trading performance
        """
        trades = self.get_user_trades(user_id)
        
        if len(trades) < 10:
            return {
                'status': 'insufficient_data',
                'message': f'Keep trading! Need at least 10 trades to analyze. You have {len(trades)} trades.',
                'suggestions': [],
                'quick_tips': [
                    'Start with paper trading to learn',
                    'Use stop losses on every trade',
                    'Don\'t risk more than 2% per trade',
                    'Follow the trend - trend is your friend'
                ]
            }
        
        # Calculate all metrics
        analysis = {
            'win_rate': self.calculate_win_rate(trades),
            'avg_win': self.calculate_avg_win(trades),
            'avg_loss': self.calculate_avg_loss(trades),
            'profit_factor': self.calculate_profit_factor(trades),
            'max_drawdown': self.calculate_max_drawdown(trades),
            'avg_hold_time': self.calculate_avg_hold_time(trades),
            'best_trading_times': self.find_best_times(trades),
            'best_symbols': self.find_best_symbols(trades),
            'worst_symbols': self.find_worst_symbols(trades),
            'common_mistakes': self.find_mistakes(trades),
            'trading_pattern': self.detect_trading_pattern(trades),
            'risk_score': self.calculate_risk_score(trades)
        }
        
        # Generate suggestions
        suggestions = self.generate_suggestions(analysis)
        
        # Calculate grade
        grade = self.calculate_grade(analysis)
        
        return {
            'status': 'success',
            'analysis': analysis,
            'suggestions': suggestions,
            'grade': grade,
            'total_trades': len(trades)
        }
    
    def get_user_trades(self, user_id):
        """
        Get all closed trades for user
        """
        trades = list(self.db.db['trades'].find({
            'user_id': str(user_id),
            'status': 'closed'
        }).sort('timestamp', -1).limit(100))
        
        return trades
    
    def calculate_win_rate(self, trades):
        """Calculate win rate"""
        if not trades:
            return 0
        winning = sum(1 for t in trades if t.get('pnl', 0) > 0)
        return (winning / len(trades)) * 100
    
    def calculate_avg_win(self, trades):
        """Calculate average winning trade"""
        wins = [t['pnl'] for t in trades if t.get('pnl', 0) > 0]
        return np.mean(wins) if wins else 0
    
    def calculate_avg_loss(self, trades):
        """Calculate average losing trade"""
        losses = [abs(t['pnl']) for t in trades if t.get('pnl', 0) < 0]
        return np.mean(losses) if losses else 0
    
    def calculate_profit_factor(self, trades):
        """Calculate profit factor"""
        total_wins = sum(t['pnl'] for t in trades if t.get('pnl', 0) > 0)
        total_losses = abs(sum(t['pnl'] for t in trades if t.get('pnl', 0) < 0))
        
        if total_losses == 0:
            return float('inf') if total_wins > 0 else 0
        
        return total_wins / total_losses
    
    def calculate_max_drawdown(self, trades):
        """Calculate maximum drawdown"""
        if not trades:
            return 0
        
        cumulative = 0
        peak = 0
        max_dd = 0
        
        for trade in sorted(trades, key=lambda x: x.get('timestamp', datetime.utcnow())):
            cumulative += trade.get('pnl', 0)
            peak = max(peak, cumulative)
            drawdown = peak - cumulative
            max_dd = max(max_dd, drawdown)
        
        return max_dd
    
    def calculate_avg_hold_time(self, trades):
        """Calculate average hold time"""
        hold_times = []
        for trade in trades:
            if 'hold_time' in trade:
                hold_times.append(trade['hold_time'])
        
        return np.mean(hold_times) if hold_times else 0
    
    def find_best_times(self, trades):
        """Find best trading times (hours of day)"""
        time_performance = {}
        
        for trade in trades:
            timestamp = trade.get('timestamp')
            if timestamp:
                hour = timestamp.hour
                if hour not in time_performance:
                    time_performance[hour] = {'profit': 0, 'count': 0}
                time_performance[hour]['profit'] += trade.get('pnl', 0)
                time_performance[hour]['count'] += 1
        
        # Calculate average profit per hour
        hour_avg = {hour: data['profit'] / data['count'] 
                    for hour, data in time_performance.items() if data['count'] > 0}
        
        # Sort by profitability
        best_hours = sorted(hour_avg.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return [f"{hour:02d}:00-{hour+1:02d}:00" for hour, _ in best_hours]
    
    def find_best_symbols(self, trades):
        """Find most profitable symbols"""
        symbol_performance = {}
        
        for trade in trades:
            symbol = trade.get('symbol')
            if symbol:
                if symbol not in symbol_performance:
                    symbol_performance[symbol] = {'profit': 0, 'count': 0}
                symbol_performance[symbol]['profit'] += trade.get('pnl', 0)
                symbol_performance[symbol]['count'] += 1
        
        # Calculate average profit per symbol
        symbol_avg = {symbol: data['profit'] / data['count'] 
                     for symbol, data in symbol_performance.items() if data['count'] >= 3}
        
        # Sort by profitability
        best_symbols = sorted(symbol_avg.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return [symbol for symbol, _ in best_symbols]
    
    def find_worst_symbols(self, trades):
        """Find least profitable symbols"""
        symbol_performance = {}
        
        for trade in trades:
            symbol = trade.get('symbol')
            if symbol:
                if symbol not in symbol_performance:
                    symbol_performance[symbol] = {'profit': 0, 'count': 0}
                symbol_performance[symbol]['profit'] += trade.get('pnl', 0)
                symbol_performance[symbol]['count'] += 1
        
        # Calculate average profit per symbol
        symbol_avg = {symbol: data['profit'] / data['count'] 
                     for symbol, data in symbol_performance.items() if data['count'] >= 3}
        
        # Sort by losses
        worst_symbols = sorted(symbol_avg.items(), key=lambda x: x[1])[:3]
        
        return [symbol for symbol, _ in worst_symbols if worst_symbols[0][1] < 0]
    
    def find_mistakes(self, trades):
        """Identify common trading mistakes"""
        mistakes = []
        
        wins = [t for t in trades if t.get('pnl', 0) > 0]
        losses = [t for t in trades if t.get('pnl', 0) < 0]
        
        # Cutting winners too early
        if wins:
            avg_win_time = np.mean([t.get('hold_time', 3600) for t in wins])
            if avg_win_time < 3600:  # Less than 1 hour
                mistakes.append({
                    'type': 'cutting_winners_early',
                    'severity': 'MEDIUM',
                    'description': 'Taking profits too quickly'
                })
        
        # Letting losers run
        if losses and wins:
            avg_loss_time = np.mean([t.get('hold_time', 3600) for t in losses])
            avg_win_time = np.mean([t.get('hold_time', 3600) for t in wins])
            if avg_loss_time > avg_win_time * 1.5:
                mistakes.append({
                    'type': 'letting_losers_run',
                    'severity': 'HIGH',
                    'description': 'Holding losing trades too long'
                })
        
        # Over-trading
        if len(trades) > 50:  # More than 50 trades in analysis period
            win_rate = self.calculate_win_rate(trades)
            if win_rate < 55:
                mistakes.append({
                    'type': 'overtrading',
                    'severity': 'MEDIUM',
                    'description': 'Trading too frequently with low win rate'
                })
        
        # Poor risk/reward
        avg_win = self.calculate_avg_win(trades)
        avg_loss = self.calculate_avg_loss(trades)
        if avg_loss > avg_win:
            mistakes.append({
                'type': 'poor_risk_reward',
                'severity': 'HIGH',
                'description': 'Average losses bigger than average wins'
            })
        
        return mistakes
    
    def detect_trading_pattern(self, trades):
        """Detect user's trading pattern"""
        avg_hold = self.calculate_avg_hold_time(trades)
        
        if avg_hold < 3600:  # < 1 hour
            return 'scalper'
        elif avg_hold < 14400:  # < 4 hours
            return 'day_trader'
        elif avg_hold < 86400:  # < 1 day
            return 'swing_trader'
        else:
            return 'position_trader'
    
    def calculate_risk_score(self, trades):
        """Calculate risk score 0-100"""
        if not trades:
            return 50
        
        # Factors
        max_dd = self.calculate_max_drawdown(trades)
        win_rate = self.calculate_win_rate(trades)
        profit_factor = self.calculate_profit_factor(trades)
        
        # Calculate score (lower is riskier)
        risk = 100
        
        # High drawdown = more risk
        if max_dd > 500:  # $500+ drawdown
            risk -= 30
        elif max_dd > 200:
            risk -= 15
        
        # Low win rate = more risk
        if win_rate < 40:
            risk -= 25
        elif win_rate < 50:
            risk -= 10
        
        # Poor profit factor = more risk
        if profit_factor < 1:
            risk -= 30
        elif profit_factor < 1.5:
            risk -= 15
        
        return max(min(risk, 100), 0)
    
    def generate_suggestions(self, analysis):
        """Generate personalized suggestions"""
        suggestions = []
        
        # Win rate suggestions
        if analysis['win_rate'] < 50:
            suggestions.append({
                'priority': 'HIGH',
                'category': 'Strategy',
                'issue': 'Low Win Rate',
                'current': f"{analysis['win_rate']:.1f}%",
                'target': '60%+',
                'suggestion': 'Wait for stronger signals. Use multi-timeframe confirmation before entering trades.',
                'expected_improvement': '+10-15% win rate',
                'action_items': [
                    'Check 1h and 4h charts before trading',
                    'Only trade when RSI confirms direction',
                    'Wait for trend alignment across timeframes'
                ]
            })
        
        # Risk/Reward suggestions
        if analysis['avg_loss'] > analysis['avg_win']:
            suggestions.append({
                'priority': 'HIGH',
                'category': 'Risk Management',
                'issue': 'Poor Risk/Reward Ratio',
                'current': f"Win: ${analysis['avg_win']:.2f}, Loss: ${analysis['avg_loss']:.2f}",
                'target': 'Win > 2x Loss',
                'suggestion': 'Use tighter stop losses. Let winners run with trailing stops.',
                'expected_improvement': 'Better profitability even with same win rate',
                'action_items': [
                    'Set stop loss at 2% maximum',
                    'Use trailing stop to lock in profits',
                    'Target 4%+ profit on each trade'
                ]
            })
        
        # Timing suggestions
        if analysis['best_trading_times']:
            best_time = analysis['best_trading_times'][0]
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'Timing',
                'issue': 'Suboptimal Trading Hours',
                'current': 'Trading at random times',
                'target': f"Focus on {best_time}",
                'suggestion': f"Your most profitable time is {best_time}. Concentrate trading during these hours.",
                'expected_improvement': '+5-10% win rate',
                'action_items': [
                    f'Schedule trading for {best_time}',
                    'Avoid trading during your worst hours',
                    'Set alerts for opportunities during peak times'
                ]
            })
        
        # Symbol selection
        if analysis['best_symbols']:
            best_symbol = analysis['best_symbols'][0]
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'Symbol Selection',
                'issue': 'Trading Too Many Pairs',
                'current': 'Spreading across multiple symbols',
                'target': f"Focus on {best_symbol}",
                'suggestion': f"Your most profitable pair is {best_symbol}. Specialize in pairs you understand best.",
                'expected_improvement': '+10-20% returns',
                'action_items': [
                    f'Focus 70% of capital on {best_symbol}',
                    'Learn the specific patterns of your best symbols',
                    'Avoid your worst performing symbols'
                ]
            })
        
        # Drawdown management
        if analysis['max_drawdown'] > 200:
            suggestions.append({
                'priority': 'HIGH',
                'category': 'Risk Management',
                'issue': 'Large Drawdowns',
                'current': f"${analysis['max_drawdown']:.2f} max drawdown",
                'target': '<$100',
                'suggestion': 'Reduce position sizes. Use Kelly Criterion for optimal sizing.',
                'expected_improvement': 'Reduced risk, smoother equity curve',
                'action_items': [
                    'Reduce position size to 10% of capital',
                    'Never risk more than 2% on single trade',
                    'Take a break after 3 consecutive losses'
                ]
            })
        
        # Pattern-specific suggestions
        pattern = analysis['trading_pattern']
        if pattern == 'scalper' and analysis['win_rate'] < 60:
            suggestions.append({
                'priority': 'MEDIUM',
                'category': 'Strategy',
                'issue': 'Scalping Requires High Win Rate',
                'current': f"{analysis['win_rate']:.1f}% win rate",
                'target': '65%+ for scalping',
                'suggestion': 'Scalping requires 60%+ win rate. Consider swing trading for better results.',
                'expected_improvement': 'Better risk/reward, less stress',
                'action_items': [
                    'Hold trades for 4+ hours instead of minutes',
                    'Use wider stops and targets',
                    'Focus on quality over quantity'
                ]
            })
        
        # Profit factor
        if analysis['profit_factor'] < 1.5:
            suggestions.append({
                'priority': 'HIGH',
                'category': 'Overall Performance',
                'issue': 'Low Profit Factor',
                'current': f"{analysis['profit_factor']:.2f}",
                'target': '2.0+',
                'suggestion': 'Cut losses faster and let winners run longer.',
                'expected_improvement': 'Significantly better profitability',
                'action_items': [
                    'Exit immediately when stop loss hits',
                    'Use trailing stop for winning trades',
                    'Don\'t take profits until target hit'
                ]
            })
        
        return suggestions
    
    def calculate_grade(self, analysis):
        """Calculate overall trading grade A-F"""
        score = 0
        max_score = 0
        
        # Win rate (30 points)
        max_score += 30
        if analysis['win_rate'] >= 65:
            score += 30
        elif analysis['win_rate'] >= 55:
            score += 20
        elif analysis['win_rate'] >= 45:
            score += 10
        
        # Profit factor (30 points)
        max_score += 30
        if analysis['profit_factor'] >= 2.5:
            score += 30
        elif analysis['profit_factor'] >= 2.0:
            score += 25
        elif analysis['profit_factor'] >= 1.5:
            score += 15
        elif analysis['profit_factor'] >= 1.0:
            score += 5
        
        # Risk/reward (20 points)
        max_score += 20
        if analysis['avg_win'] > analysis['avg_loss'] * 2:
            score += 20
        elif analysis['avg_win'] > analysis['avg_loss']:
            score += 10
        
        # Drawdown management (20 points)
        max_score += 20
        if analysis['max_drawdown'] < 100:
            score += 20
        elif analysis['max_drawdown'] < 250:
            score += 10
        elif analysis['max_drawdown'] < 500:
            score += 5
        
        # Calculate percentage
        percent = (score / max_score) * 100
        
        # Assign grade
        if percent >= 90:
            grade = 'A'
        elif percent >= 80:
            grade = 'B'
        elif percent >= 70:
            grade = 'C'
        elif percent >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'grade': grade,
            'score': score,
            'max_score': max_score,
            'percent': percent
        }
