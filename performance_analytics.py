"""
Advanced Performance Analytics and Reporting
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class PerformanceAnalytics:
    """
    Comprehensive performance tracking and analytics
    """
    
    def __init__(self, database):
        self.db = database
        
    def get_performance_summary(self, user_id=None, days=30):
        """Get comprehensive performance summary"""
        # Get trades
        if user_id:
            trades = list(self.db.trades.find({
                'user_id': user_id,
                'status': 'closed',
                'exit_time': {'$gte': datetime.now() - timedelta(days=days)}
            }))
        else:
            trades = list(self.db.trades.find({
                'status': 'closed',
                'exit_time': {'$gte': datetime.now() - timedelta(days=days)}
            }))
        
        if not trades:
            return self._empty_summary()
        
        df = pd.DataFrame(trades)
        
        # Calculate metrics
        summary = {
            'overview': self._calculate_overview(df),
            'profitability': self._calculate_profitability(df),
            'risk_metrics': self._calculate_risk_metrics(df),
            'strategy_performance': self._calculate_strategy_performance(df),
            'time_analysis': self._calculate_time_analysis(df),
            'symbol_performance': self._calculate_symbol_performance(df),
            'recent_trades': self._get_recent_trades(df, limit=10)
        }
        
        return summary
    
    def _calculate_overview(self, df):
        """Calculate overview metrics"""
        total_trades = len(df)
        winning_trades = len(df[df['pnl'] > 0])
        losing_trades = len(df[df['pnl'] <= 0])
        
        total_pnl = df['pnl'].sum()
        total_fees = df['fees'].sum() if 'fees' in df.columns else 0
        net_pnl = total_pnl - total_fees
        
        avg_trade_duration = (df['exit_time'] - df['entry_time']).mean()
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            'total_pnl': float(total_pnl),
            'net_pnl': float(net_pnl),
            'total_fees': float(total_fees),
            'avg_trade_duration_hours': avg_trade_duration.total_seconds() / 3600 if not pd.isna(avg_trade_duration) else 0
        }
    
    def _calculate_profitability(self, df):
        """Calculate profitability metrics"""
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] <= 0]
        
        total_wins = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        total_losses = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0
        
        largest_win = winning_trades['pnl'].max() if len(winning_trades) > 0 else 0
        largest_loss = abs(losing_trades['pnl'].min()) if len(losing_trades) > 0 else 0
        
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Calculate consecutive wins/losses
        df_sorted = df.sort_values('exit_time')
        win_streak = 0
        loss_streak = 0
        max_win_streak = 0
        max_loss_streak = 0
        
        for pnl in df_sorted['pnl']:
            if pnl > 0:
                win_streak += 1
                loss_streak = 0
                max_win_streak = max(max_win_streak, win_streak)
            else:
                loss_streak += 1
                win_streak = 0
                max_loss_streak = max(max_loss_streak, loss_streak)
        
        return {
            'total_wins': float(total_wins),
            'total_losses': float(total_losses),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'largest_win': float(largest_win),
            'largest_loss': float(largest_loss),
            'profit_factor': float(profit_factor) if profit_factor != float('inf') else 999,
            'win_loss_ratio': float(avg_win / avg_loss) if avg_loss > 0 else 0,
            'max_consecutive_wins': max_win_streak,
            'max_consecutive_losses': max_loss_streak
        }
    
    def _calculate_risk_metrics(self, df):
        """Calculate risk-adjusted metrics"""
        returns = df['pnl_pct'] if 'pnl_pct' in df.columns else df['pnl'] / df['entry_value']
        
        # Sharpe Ratio (assuming 2% risk-free rate)
        risk_free_rate = 0.02 / 252  # Daily risk-free rate
        excess_returns = returns - risk_free_rate
        sharpe_ratio = (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Sortino Ratio (only downside deviation)
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
        sortino_ratio = (excess_returns.mean() / downside_std) * np.sqrt(252) if downside_std > 0 else 0
        
        # Maximum Drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5)
        
        # Calmar Ratio
        annual_return = returns.mean() * 252
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        return {
            'sharpe_ratio': float(sharpe_ratio),
            'sortino_ratio': float(sortino_ratio),
            'max_drawdown': float(max_drawdown * 100),
            'var_95': float(var_95 * 100),
            'calmar_ratio': float(calmar_ratio),
            'volatility': float(returns.std() * np.sqrt(252) * 100)
        }
    
    def _calculate_strategy_performance(self, df):
        """Calculate performance by strategy"""
        if 'strategy' not in df.columns:
            return {}
        
        strategy_stats = {}
        for strategy in df['strategy'].unique():
            strategy_df = df[df['strategy'] == strategy]
            
            total_trades = len(strategy_df)
            winning_trades = len(strategy_df[strategy_df['pnl'] > 0])
            total_pnl = strategy_df['pnl'].sum()
            
            strategy_stats[strategy] = {
                'total_trades': total_trades,
                'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                'total_pnl': float(total_pnl),
                'avg_pnl': float(strategy_df['pnl'].mean())
            }
        
        return strategy_stats
    
    def _calculate_time_analysis(self, df):
        """Analyze performance by time periods"""
        df['hour'] = pd.to_datetime(df['entry_time']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['entry_time']).dt.dayofweek
        
        # Performance by hour
        hourly_performance = df.groupby('hour')['pnl'].agg(['sum', 'count', 'mean']).to_dict('index')
        
        # Performance by day of week
        daily_performance = df.groupby('day_of_week')['pnl'].agg(['sum', 'count', 'mean']).to_dict('index')
        
        # Best and worst hours
        best_hour = df.groupby('hour')['pnl'].sum().idxmax()
        worst_hour = df.groupby('hour')['pnl'].sum().idxmin()
        
        return {
            'hourly_performance': {int(k): {
                'total_pnl': float(v['sum']),
                'trades': int(v['count']),
                'avg_pnl': float(v['mean'])
            } for k, v in hourly_performance.items()},
            'daily_performance': {int(k): {
                'total_pnl': float(v['sum']),
                'trades': int(v['count']),
                'avg_pnl': float(v['mean'])
            } for k, v in daily_performance.items()},
            'best_trading_hour': int(best_hour),
            'worst_trading_hour': int(worst_hour)
        }
    
    def _calculate_symbol_performance(self, df):
        """Calculate performance by trading symbol"""
        symbol_stats = {}
        
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol]
            
            total_trades = len(symbol_df)
            winning_trades = len(symbol_df[symbol_df['pnl'] > 0])
            total_pnl = symbol_df['pnl'].sum()
            
            symbol_stats[symbol] = {
                'total_trades': total_trades,
                'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
                'total_pnl': float(total_pnl),
                'avg_pnl': float(symbol_df['pnl'].mean()),
                'best_trade': float(symbol_df['pnl'].max()),
                'worst_trade': float(symbol_df['pnl'].min())
            }
        
        return symbol_stats
    
    def _get_recent_trades(self, df, limit=10):
        """Get recent trades"""
        recent = df.sort_values('exit_time', ascending=False).head(limit)
        
        trades = []
        for _, trade in recent.iterrows():
            trades.append({
                'symbol': trade['symbol'],
                'signal': trade['signal'],
                'entry_price': float(trade['entry_price']),
                'exit_price': float(trade['exit_price']),
                'pnl': float(trade['pnl']),
                'pnl_pct': float(trade.get('pnl_pct', 0)),
                'entry_time': trade['entry_time'].isoformat() if isinstance(trade['entry_time'], datetime) else str(trade['entry_time']),
                'exit_time': trade['exit_time'].isoformat() if isinstance(trade['exit_time'], datetime) else str(trade['exit_time']),
                'strategy': trade.get('strategy', 'unknown')
            })
        
        return trades
    
    def _empty_summary(self):
        """Return empty summary when no trades"""
        return {
            'overview': {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'net_pnl': 0,
                'total_fees': 0,
                'avg_trade_duration_hours': 0
            },
            'profitability': {},
            'risk_metrics': {},
            'strategy_performance': {},
            'time_analysis': {},
            'symbol_performance': {},
            'recent_trades': []
        }
    
    def generate_report(self, user_id=None, period='month'):
        """Generate comprehensive performance report"""
        days_map = {
            'week': 7,
            'month': 30,
            'quarter': 90,
            'year': 365
        }
        
        days = days_map.get(period, 30)
        summary = self.get_performance_summary(user_id, days)
        
        # Generate insights
        insights = self._generate_insights(summary)
        
        report = {
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'summary': summary,
            'insights': insights,
            'recommendations': self._generate_recommendations(summary)
        }
        
        return report
    
    def _generate_insights(self, summary):
        """Generate insights from performance data"""
        insights = []
        
        overview = summary.get('overview', {})
        profitability = summary.get('profitability', {})
        risk_metrics = summary.get('risk_metrics', {})
        
        # Win rate insights
        win_rate = overview.get('win_rate', 0)
        if win_rate > 60:
            insights.append({
                'type': 'positive',
                'message': f'Excellent win rate of {win_rate:.1f}%! Your strategy is performing well.'
            })
        elif win_rate < 40:
            insights.append({
                'type': 'warning',
                'message': f'Win rate of {win_rate:.1f}% is below optimal. Consider reviewing your entry criteria.'
            })
        
        # Profit factor insights
        profit_factor = profitability.get('profit_factor', 0)
        if profit_factor > 2:
            insights.append({
                'type': 'positive',
                'message': f'Strong profit factor of {profit_factor:.2f}. Your winners are significantly larger than losers.'
            })
        elif profit_factor < 1:
            insights.append({
                'type': 'warning',
                'message': f'Profit factor of {profit_factor:.2f} indicates losses exceed wins. Review your risk management.'
            })
        
        # Risk-adjusted returns
        sharpe_ratio = risk_metrics.get('sharpe_ratio', 0)
        if sharpe_ratio > 1.5:
            insights.append({
                'type': 'positive',
                'message': f'Excellent risk-adjusted returns (Sharpe: {sharpe_ratio:.2f})'
            })
        elif sharpe_ratio < 0.5:
            insights.append({
                'type': 'warning',
                'message': f'Low risk-adjusted returns (Sharpe: {sharpe_ratio:.2f}). Consider reducing risk.'
            })
        
        return insights
    
    def _generate_recommendations(self, summary):
        """Generate actionable recommendations"""
        recommendations = []
        
        profitability = summary.get('profitability', {})
        risk_metrics = summary.get('risk_metrics', {})
        
        # Win/loss ratio recommendation
        win_loss_ratio = profitability.get('win_loss_ratio', 0)
        if win_loss_ratio < 1.5:
            recommendations.append({
                'priority': 'high',
                'action': 'Improve win/loss ratio',
                'suggestion': 'Consider widening take-profit targets or tightening stop-losses'
            })
        
        # Drawdown recommendation
        max_drawdown = abs(risk_metrics.get('max_drawdown', 0))
        if max_drawdown > 15:
            recommendations.append({
                'priority': 'high',
                'action': 'Reduce drawdown',
                'suggestion': 'Implement stricter position sizing and daily loss limits'
            })
        
        # Diversification recommendation
        symbol_performance = summary.get('symbol_performance', {})
        if len(symbol_performance) < 3:
            recommendations.append({
                'priority': 'medium',
                'action': 'Increase diversification',
                'suggestion': 'Trade more symbols to reduce concentration risk'
            })
        
        return recommendations
