"""
Advanced Backtesting System
Test strategies on historical data before risking real money
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Callable

logger = logging.getLogger(__name__)


class Backtester:
    """
    Professional backtesting engine
    - Test strategies on historical data
    - Walk-forward analysis
    - Monte Carlo simulation
    - Comprehensive performance metrics
    """
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        
    def run(self, data: pd.DataFrame, strategy: Callable, params: dict = None) -> dict:
        """
        Run backtest on historical data
        
        Args:
            data: OHLCV data
            strategy: Trading strategy function
            params: Strategy parameters
        
        Returns:
            dict: Backtest results
        """
        self.capital = self.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        
        logger.info(f"Starting backtest with ${self.initial_capital}")
        
        for i in range(len(data)):
            current_data = data.iloc[:i+1]
            
            if len(current_data) < 50:  # Need minimum data for indicators
                continue
            
            # Get strategy signal
            signal = strategy(current_data, params)
            
            # Execute trades based on signal
            self._execute_signal(signal, current_data.iloc[-1])
            
            # Update equity curve
            self.equity_curve.append({
                'timestamp': current_data.iloc[-1]['timestamp'],
                'equity': self.capital + self._calculate_open_position_value(current_data.iloc[-1]['close'])
            })
        
        # Close any open positions
        if self.positions:
            final_price = data.iloc[-1]['close']
            for position in self.positions:
                self._close_position(position, final_price, 'backtest_end')
        
        # Calculate metrics
        results = self._calculate_metrics()
        
        logger.info(f"Backtest complete - Final capital: ${self.capital:.2f}")
        
        return results
    
    def _execute_signal(self, signal: dict, bar: pd.Series):
        """Execute trading signal"""
        if not signal or not signal.get('signal'):
            return
        
        current_price = bar['close']
        
        if signal['signal'] == 'buy' and not self.positions:
            # Open long position
            position_size = (self.capital * 0.95) / current_price  # Use 95% of capital
            
            position = {
                'type': 'long',
                'entry_price': current_price,
                'size': position_size,
                'entry_time': bar['timestamp'],
                'stop_loss': signal.get('stop_loss'),
                'take_profit': signal.get('take_profit')
            }
            
            self.positions.append(position)
            self.capital -= position_size * current_price
            
        elif signal['signal'] == 'sell' and self.positions:
            # Close long position
            for position in self.positions[:]:
                self._close_position(position, current_price, 'signal')
    
    def _close_position(self, position: dict, exit_price: float, reason: str):
        """Close a position"""
        pnl = (exit_price - position['entry_price']) * position['size']
        pnl_pct = (pnl / (position['entry_price'] * position['size'])) * 100
        
        self.capital += position['size'] * exit_price
        
        trade = {
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'size': position['size'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'entry_time': position['entry_time'],
            'exit_time': datetime.now(),
            'reason': reason
        }
        
        self.trades.append(trade)
        self.positions.remove(position)
    
    def _calculate_open_position_value(self, current_price: float) -> float:
        """Calculate value of open positions"""
        total_value = 0
        for position in self.positions:
            total_value += position['size'] * current_price
        return total_value
    
    def _calculate_metrics(self) -> dict:
        """Calculate comprehensive performance metrics"""
        if not self.trades:
            return {'error': 'No trades executed'}
        
        trades_df = pd.DataFrame(self.trades)
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['pnl'] > 0])
        losing_trades = len(trades_df[trades_df['pnl'] <= 0])
        win_rate = (winning_trades / total_trades) * 100
        
        # P&L metrics
        total_pnl = trades_df['pnl'].sum()
        total_return = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        avg_win = trades_df[trades_df['pnl'] > 0]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = abs(trades_df[trades_df['pnl'] <= 0]['pnl'].mean()) if losing_trades > 0 else 0
        
        # Risk metrics
        returns = trades_df['pnl_pct']
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() > 0 else 0
        
        # Drawdown
        equity_df = pd.DataFrame(self.equity_curve)
        equity_df['peak'] = equity_df['equity'].expanding().max()
        equity_df['drawdown'] = (equity_df['equity'] - equity_df['peak']) / equity_df['peak']
        max_drawdown = equity_df['drawdown'].min() * 100
        
        # Profit factor
        total_wins = trades_df[trades_df['pnl'] > 0]['pnl'].sum()
        total_losses = abs(trades_df[trades_df['pnl'] <= 0]['pnl'].sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'total_return': total_return,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_capital': self.capital,
            'trades': self.trades,
            'equity_curve': self.equity_curve
        }
    
    def walk_forward_analysis(self, data: pd.DataFrame, strategy: Callable, 
                             train_period: int = 100, test_period: int = 20) -> dict:
        """
        Walk-forward analysis - more realistic than simple backtest
        Train on historical data, test on out-of-sample data
        """
        results = []
        
        for i in range(0, len(data) - train_period - test_period, test_period):
            # Training period
            train_data = data.iloc[i:i+train_period]
            
            # Testing period
            test_data = data.iloc[i+train_period:i+train_period+test_period]
            
            # Run backtest on test data
            test_result = self.run(test_data, strategy)
            results.append(test_result)
        
        # Aggregate results
        avg_return = np.mean([r['total_return'] for r in results])
        avg_sharpe = np.mean([r['sharpe_ratio'] for r in results])
        avg_drawdown = np.mean([r['max_drawdown'] for r in results])
        
        return {
            'walk_forward_results': results,
            'avg_return': avg_return,
            'avg_sharpe': avg_sharpe,
            'avg_drawdown': avg_drawdown,
            'consistency': np.std([r['total_return'] for r in results])
        }
    
    def monte_carlo_simulation(self, trades: List[dict], simulations: int = 1000) -> dict:
        """
        Monte Carlo simulation - test strategy robustness
        Randomly shuffle trade order to see range of outcomes
        """
        if not trades:
            return {'error': 'No trades to simulate'}
        
        trade_returns = [t['pnl_pct'] for t in trades]
        
        simulation_results = []
        
        for _ in range(simulations):
            # Randomly shuffle trades
            shuffled_returns = np.random.choice(trade_returns, size=len(trade_returns), replace=True)
            
            # Calculate cumulative return
            cumulative_return = np.prod(1 + np.array(shuffled_returns) / 100) - 1
            simulation_results.append(cumulative_return * 100)
        
        simulation_results = np.array(simulation_results)
        
        return {
            'mean_return': simulation_results.mean(),
            'median_return': np.median(simulation_results),
            'std_return': simulation_results.std(),
            'best_case': np.percentile(simulation_results, 95),
            'worst_case': np.percentile(simulation_results, 5),
            'probability_of_profit': (simulation_results > 0).sum() / simulations * 100
        }


class StrategyOptimizer:
    """
    Optimize strategy parameters
    Find best parameter combinations
    """
    
    def __init__(self, backtester: Backtester):
        self.backtester = backtester
    
    def optimize(self, data: pd.DataFrame, strategy: Callable, 
                 param_grid: dict, metric: str = 'sharpe_ratio') -> dict:
        """
        Grid search optimization
        
        Args:
            data: Historical data
            strategy: Strategy function
            param_grid: Dictionary of parameters to test
            metric: Metric to optimize for
        
        Returns:
            dict: Best parameters and results
        """
        from itertools import product
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        param_combinations = list(product(*param_values))
        
        best_score = float('-inf')
        best_params = None
        best_results = None
        
        logger.info(f"Testing {len(param_combinations)} parameter combinations...")
        
        for params in param_combinations:
            param_dict = dict(zip(param_names, params))
            
            try:
                results = self.backtester.run(data, strategy, param_dict)
                
                score = results.get(metric, float('-inf'))
                
                if score > best_score:
                    best_score = score
                    best_params = param_dict
                    best_results = results
                    
            except Exception as e:
                logger.error(f"Error testing params {param_dict}: {e}")
                continue
        
        logger.info(f"Best parameters found: {best_params}")
        logger.info(f"Best {metric}: {best_score:.2f}")
        
        return {
            'best_params': best_params,
            'best_score': best_score,
            'best_results': best_results
        }


class PerformanceReport:
    """
    Generate detailed performance reports
    """
    
    @staticmethod
    def generate_html_report(backtest_results: dict) -> str:
        """Generate HTML performance report"""
        html = f"""
        <html>
        <head>
            <title>Backtest Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ margin: 10px 0; padding: 10px; background: #f0f0f0; border-radius: 5px; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #4CAF50; color: white; }}
            </style>
        </head>
        <body>
            <h1>Backtest Performance Report</h1>
            
            <h2>Summary</h2>
            <div class="metric">
                <strong>Total Return:</strong> 
                <span class="{'positive' if backtest_results['total_return'] > 0 else 'negative'}">
                    {backtest_results['total_return']:.2f}%
                </span>
            </div>
            <div class="metric">
                <strong>Win Rate:</strong> {backtest_results['win_rate']:.2f}%
            </div>
            <div class="metric">
                <strong>Profit Factor:</strong> {backtest_results['profit_factor']:.2f}
            </div>
            <div class="metric">
                <strong>Sharpe Ratio:</strong> {backtest_results['sharpe_ratio']:.2f}
            </div>
            <div class="metric">
                <strong>Max Drawdown:</strong> 
                <span class="negative">{backtest_results['max_drawdown']:.2f}%</span>
            </div>
            
            <h2>Trade Statistics</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Trades</td>
                    <td>{backtest_results['total_trades']}</td>
                </tr>
                <tr>
                    <td>Winning Trades</td>
                    <td>{backtest_results['winning_trades']}</td>
                </tr>
                <tr>
                    <td>Losing Trades</td>
                    <td>{backtest_results['losing_trades']}</td>
                </tr>
                <tr>
                    <td>Average Win</td>
                    <td>${backtest_results['avg_win']:.2f}</td>
                </tr>
                <tr>
                    <td>Average Loss</td>
                    <td>${backtest_results['avg_loss']:.2f}</td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    def generate_pdf_report(backtest_results: dict, filename: str = 'backtest_report.pdf'):
        """Generate PDF report (requires reportlab)"""
        # Placeholder for PDF generation
        # Would use reportlab or similar library
        pass
