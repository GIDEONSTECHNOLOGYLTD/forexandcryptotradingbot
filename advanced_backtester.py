"""
Advanced Backtesting System
Walk-forward analysis, Monte Carlo simulation, and comprehensive performance metrics
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

from ai_strategy import AITradingStrategy
from advanced_risk_manager import AdvancedRiskManager
import config


class AdvancedBacktester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.strategy = AITradingStrategy()
        self.results = []
        
    def fetch_historical_data(self, symbol, days=365):
        """Fetch historical data for backtesting"""
        try:
            import ccxt
            exchange = ccxt.okx({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            
            # Calculate start time
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)
            
            # Fetch OHLCV data
            since = int(start_time.timestamp() * 1000)
            ohlcv = exchange.fetch_ohlcv(symbol, '1h', since=since, limit=1000)
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return self._generate_synthetic_data(symbol, days)
    
    def _generate_synthetic_data(self, symbol, days=365):
        """Generate synthetic price data for testing"""
        np.random.seed(42)  # For reproducible results
        
        # Generate realistic price movements
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), 
                             end=datetime.now(), freq='1H')
        
        # Start with a base price
        base_price = 100.0
        returns = np.random.normal(0.0001, 0.02, len(dates))  # Small positive drift with volatility
        
        # Add some trend and cycles
        trend = np.linspace(0, 0.5, len(dates))  # Upward trend
        cycle = 0.1 * np.sin(np.linspace(0, 4*np.pi, len(dates)))  # Cyclical component
        
        returns += trend / len(dates) + cycle / len(dates)
        
        # Calculate prices
        prices = [base_price]
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        # Create OHLCV data
        df = pd.DataFrame(index=dates)
        df['close'] = prices
        df['open'] = df['close'].shift(1).fillna(df['close'].iloc[0])
        
        # Generate high/low based on volatility
        volatility = np.random.uniform(0.005, 0.02, len(df))
        df['high'] = df[['open', 'close']].max(axis=1) * (1 + volatility)
        df['low'] = df[['open', 'close']].min(axis=1) * (1 - volatility)
        
        # Generate volume
        df['volume'] = np.random.uniform(1000000, 10000000, len(df))
        
        return df
    
    def run_backtest(self, symbol, start_date=None, end_date=None, walk_forward=True):
        """Run comprehensive backtest with walk-forward analysis"""
        print(f"\n🔄 Running Advanced Backtest for {symbol}")
        print("="*60)
        
        # Fetch data
        df = self.fetch_historical_data(symbol, days=365)
        if df is None or len(df) < 200:
            print("❌ Insufficient data for backtesting")
            return None
        
        # Filter by date range if specified
        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]
        
        if walk_forward:
            return self._walk_forward_analysis(df, symbol)
        else:
            return self._single_period_backtest(df, symbol)
    
    def _walk_forward_analysis(self, df, symbol, window_size=100, step_size=20):
        """Perform walk-forward analysis"""
        print("📈 Performing Walk-Forward Analysis...")
        
        results = []
        total_periods = (len(df) - window_size) // step_size
        
        for i in range(0, len(df) - window_size, step_size):
            period_start = i
            period_end = i + window_size
            
            if period_end >= len(df):
                break
            
            # Training data (for ML model)
            train_data = df.iloc[max(0, period_start-200):period_start]
            
            # Test data
            test_data = df.iloc[period_start:period_end]
            
            print(f"Period {len(results)+1}/{total_periods}: {test_data.index[0].strftime('%Y-%m-%d')} to {test_data.index[-1].strftime('%Y-%m-%d')}")
            
            # Train strategy on historical data
            if len(train_data) >= 50:
                self.strategy.train_ml_model(train_data, symbol)
            
            # Run backtest on test period
            period_result = self._single_period_backtest(test_data, symbol, verbose=False)
            if period_result:
                period_result['period'] = len(results) + 1
                period_result['start_date'] = test_data.index[0]
                period_result['end_date'] = test_data.index[-1]
                results.append(period_result)
        
        # Aggregate results
        return self._aggregate_walk_forward_results(results, symbol)
    
    def _single_period_backtest(self, df, symbol, verbose=True):
        """Run backtest for a single period"""
        risk_manager = AdvancedRiskManager(self.initial_capital)
        
        # Add indicators
        df = self.strategy.add_advanced_indicators(df)
        
        trades = []
        equity_curve = [self.initial_capital]
        
        for i in range(200, len(df)):  # Start after indicators are stable
            current_data = df.iloc[:i+1]
            current_row = df.iloc[i]
            current_price = current_row['close']
            current_time = df.index[i]
            
            # Update open positions
            for pos_symbol in list(risk_manager.open_positions.keys()):
                risk_manager.update_position_tracking(pos_symbol, current_price)
                
                # Check exit conditions
                exit_reason = risk_manager.check_stop_loss_take_profit(pos_symbol, current_price)
                if exit_reason:
                    trade_record = risk_manager.close_position(pos_symbol, current_price)
                    if trade_record:
                        trade_record['exit_time'] = current_time
                        trade_record['exit_reason'] = exit_reason
                        trades.append(trade_record)
            
            # Check for new signals
            if symbol not in risk_manager.open_positions:
                signal, confidence, context = self.strategy.generate_advanced_signal(current_data, symbol)
                
                if signal and confidence >= 65:
                    # Calculate position size
                    volatility = context.get('volatility', 0.02)
                    correlation_risk = risk_manager.calculate_portfolio_correlation_risk(
                        symbol, list(risk_manager.open_positions.keys())
                    )
                    
                    position_size, risk_percent = risk_manager.calculate_dynamic_position_size(
                        symbol, current_price, confidence, volatility, correlation_risk
                    )
                    
                    # Check if we can trade
                    can_trade, reason = risk_manager.can_trade()
                    if can_trade:
                        # Calculate dynamic stops
                        stop_loss, stop_percent = risk_manager.calculate_dynamic_stop_loss(
                            current_price, volatility, confidence, signal
                        )
                        take_profit, tp_percent = risk_manager.calculate_dynamic_take_profit(
                            current_price, volatility, confidence, signal
                        )
                        
                        # Open position
                        position = risk_manager.open_position(symbol, signal, current_price, position_size)
                        position['stop_loss'] = stop_loss
                        position['take_profit'] = take_profit
                        position['confidence'] = confidence
                        position['entry_time'] = current_time
                        position['context'] = context
                        position['use_trailing_stop'] = True
            
            # Update equity curve
            current_capital = risk_manager.current_capital
            for position in risk_manager.open_positions.values():
                if 'unrealized_pnl' in position:
                    current_capital += position['unrealized_pnl']
            
            equity_curve.append(current_capital)
        
        # Close any remaining positions
        for symbol_pos in list(risk_manager.open_positions.keys()):
            final_price = df.iloc[-1]['close']
            trade_record = risk_manager.close_position(symbol_pos, final_price)
            if trade_record:
                trade_record['exit_time'] = df.index[-1]
                trade_record['exit_reason'] = 'backtest_end'
                trades.append(trade_record)
        
        # Calculate results
        result = self._calculate_backtest_metrics(
            trades, equity_curve, risk_manager, df.index[0], df.index[-1]
        )
        
        if verbose:
            self._display_backtest_results(result, symbol)
        
        return result
    
    def _calculate_backtest_metrics(self, trades, equity_curve, risk_manager, start_date, end_date):
        """Calculate comprehensive backtest metrics"""
        if not trades:
            return {
                'total_return': 0,
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'calmar_ratio': 0
            }
        
        # Basic metrics
        final_capital = equity_curve[-1]
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        total_wins = sum(t['pnl'] for t in winning_trades)
        total_losses = abs(sum(t['pnl'] for t in losing_trades))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Calculate drawdown
        peak = equity_curve[0]
        max_drawdown = 0
        drawdowns = []
        
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            drawdowns.append(drawdown)
            max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate Sharpe ratio
        returns = []
        for i in range(1, len(equity_curve)):
            daily_return = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(daily_return)
        
        if returns and np.std(returns) > 0:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)  # Annualized
        else:
            sharpe_ratio = 0
        
        # Calmar ratio
        days_traded = (end_date - start_date).days
        annual_return = (1 + total_return) ** (365 / days_traded) - 1 if days_traded > 0 else 0
        calmar_ratio = annual_return / max_drawdown if max_drawdown > 0 else 0
        
        # Additional metrics
        avg_trade_duration = np.mean([
            (t['exit_time'] - t['entry_time']).total_seconds() / 3600 
            for t in trades if 'exit_time' in t and 'entry_time' in t
        ]) if trades else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'calmar_ratio': calmar_ratio,
            'avg_win': np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0,
            'avg_loss': np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0,
            'avg_trade_duration_hours': avg_trade_duration,
            'final_capital': final_capital,
            'equity_curve': equity_curve,
            'trades': trades,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def _aggregate_walk_forward_results(self, results, symbol):
        """Aggregate walk-forward analysis results"""
        if not results:
            return None
        
        print(f"\n📊 Walk-Forward Analysis Results for {symbol}")
        print("="*60)
        
        # Calculate aggregate metrics
        total_returns = [r['total_return'] for r in results]
        win_rates = [r['win_rate'] for r in results]
        profit_factors = [r['profit_factor'] for r in results if r['profit_factor'] != float('inf')]
        max_drawdowns = [r['max_drawdown'] for r in results]
        sharpe_ratios = [r['sharpe_ratio'] for r in results]
        
        aggregate_result = {
            'periods_tested': len(results),
            'avg_return_per_period': np.mean(total_returns),
            'std_return_per_period': np.std(total_returns),
            'avg_win_rate': np.mean(win_rates),
            'avg_profit_factor': np.mean(profit_factors) if profit_factors else 0,
            'avg_max_drawdown': np.mean(max_drawdowns),
            'avg_sharpe_ratio': np.mean(sharpe_ratios),
            'consistency_score': len([r for r in total_returns if r > 0]) / len(total_returns),
            'best_period_return': max(total_returns),
            'worst_period_return': min(total_returns),
            'period_results': results
        }
        
        self._display_walk_forward_results(aggregate_result, symbol)
        return aggregate_result
    
    def _display_backtest_results(self, result, symbol):
        """Display backtest results"""
        print(f"\n📊 Backtest Results for {symbol}")
        print("="*50)
        print(f"Period: {result['start_date'].strftime('%Y-%m-%d')} to {result['end_date'].strftime('%Y-%m-%d')}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        print(f"Final Capital: ${result['final_capital']:,.2f}")
        print(f"Total Return: {result['total_return']:.2%}")
        print(f"Annual Return: {result['annual_return']:.2%}")
        print(f"\nTrade Statistics:")
        print(f"Total Trades: {result['total_trades']}")
        print(f"Winning Trades: {result['winning_trades']}")
        print(f"Losing Trades: {result['losing_trades']}")
        print(f"Win Rate: {result['win_rate']:.1%}")
        print(f"Profit Factor: {result['profit_factor']:.2f}")
        print(f"Avg Win: ${result['avg_win']:.2f}")
        print(f"Avg Loss: ${result['avg_loss']:.2f}")
        print(f"\nRisk Metrics:")
        print(f"Max Drawdown: {result['max_drawdown']:.2%}")
        print(f"Sharpe Ratio: {result['sharpe_ratio']:.2f}")
        print(f"Calmar Ratio: {result['calmar_ratio']:.2f}")
        print(f"Avg Trade Duration: {result['avg_trade_duration_hours']:.1f} hours")
    
    def _display_walk_forward_results(self, result, symbol):
        """Display walk-forward analysis results"""
        print(f"Periods Tested: {result['periods_tested']}")
        print(f"Average Return per Period: {result['avg_return_per_period']:.2%}")
        print(f"Return Volatility: {result['std_return_per_period']:.2%}")
        print(f"Average Win Rate: {result['avg_win_rate']:.1%}")
        print(f"Average Profit Factor: {result['avg_profit_factor']:.2f}")
        print(f"Average Max Drawdown: {result['avg_max_drawdown']:.2%}")
        print(f"Average Sharpe Ratio: {result['avg_sharpe_ratio']:.2f}")
        print(f"Consistency Score: {result['consistency_score']:.1%}")
        print(f"Best Period Return: {result['best_period_return']:.2%}")
        print(f"Worst Period Return: {result['worst_period_return']:.2%}")
        
        # Strategy robustness assessment
        if result['consistency_score'] > 0.7:
            print("✅ Strategy shows HIGH consistency across periods")
        elif result['consistency_score'] > 0.5:
            print("⚠️  Strategy shows MEDIUM consistency across periods")
        else:
            print("❌ Strategy shows LOW consistency across periods")
    
    def monte_carlo_simulation(self, symbol, num_simulations=1000):
        """Run Monte Carlo simulation for risk assessment"""
        print(f"\n🎲 Running Monte Carlo Simulation for {symbol}")
        print(f"Simulations: {num_simulations}")
        print("="*50)
        
        # Get base backtest result
        base_result = self.run_backtest(symbol, walk_forward=False)
        if not base_result or not base_result['trades']:
            print("❌ No base trades for Monte Carlo simulation")
            return None
        
        # Extract trade returns
        trade_returns = [t['pnl_percent'] / 100 for t in base_result['trades']]
        
        simulation_results = []
        
        for sim in range(num_simulations):
            # Randomly sample trades with replacement
            simulated_returns = np.random.choice(trade_returns, size=len(trade_returns), replace=True)
            
            # Calculate cumulative return
            capital = self.initial_capital
            for ret in simulated_returns:
                capital *= (1 + ret)
            
            final_return = (capital - self.initial_capital) / self.initial_capital
            simulation_results.append(final_return)
        
        # Analyze results
        simulation_results = np.array(simulation_results)
        
        monte_carlo_stats = {
            'mean_return': np.mean(simulation_results),
            'std_return': np.std(simulation_results),
            'var_95': np.percentile(simulation_results, 5),  # 95% VaR
            'var_99': np.percentile(simulation_results, 1),  # 99% VaR
            'probability_of_loss': np.sum(simulation_results < 0) / num_simulations,
            'probability_of_10_percent_loss': np.sum(simulation_results < -0.1) / num_simulations,
            'expected_shortfall_95': np.mean(simulation_results[simulation_results <= np.percentile(simulation_results, 5)]),
            'best_case': np.max(simulation_results),
            'worst_case': np.min(simulation_results)
        }
        
        self._display_monte_carlo_results(monte_carlo_stats)
        return monte_carlo_stats
    
    def _display_monte_carlo_results(self, stats):
        """Display Monte Carlo simulation results"""
        print(f"Mean Return: {stats['mean_return']:.2%}")
        print(f"Return Volatility: {stats['std_return']:.2%}")
        print(f"95% VaR: {stats['var_95']:.2%}")
        print(f"99% VaR: {stats['var_99']:.2%}")
        print(f"Probability of Loss: {stats['probability_of_loss']:.1%}")
        print(f"Probability of >10% Loss: {stats['probability_of_10_percent_loss']:.1%}")
        print(f"Expected Shortfall (95%): {stats['expected_shortfall_95']:.2%}")
        print(f"Best Case Scenario: {stats['best_case']:.2%}")
        print(f"Worst Case Scenario: {stats['worst_case']:.2%}")
        
        # Risk assessment
        if stats['probability_of_loss'] < 0.3:
            print("✅ LOW risk strategy")
        elif stats['probability_of_loss'] < 0.5:
            print("⚠️  MEDIUM risk strategy")
        else:
            print("❌ HIGH risk strategy")
    
    def compare_strategies(self, symbols, strategies=None):
        """Compare performance across multiple symbols/strategies"""
        print("\n🔍 Strategy Comparison Analysis")
        print("="*60)
        
        results = {}
        for symbol in symbols:
            print(f"\nTesting {symbol}...")
            result = self.run_backtest(symbol, walk_forward=True)
            if result:
                results[symbol] = result
        
        if not results:
            print("❌ No results to compare")
            return None
        
        # Create comparison table
        comparison_data = []
        for symbol, result in results.items():
            comparison_data.append({
                'Symbol': symbol,
                'Avg Return': f"{result['avg_return_per_period']:.2%}",
                'Win Rate': f"{result['avg_win_rate']:.1%}",
                'Profit Factor': f"{result['avg_profit_factor']:.2f}",
                'Max DD': f"{result['avg_max_drawdown']:.2%}",
                'Sharpe': f"{result['avg_sharpe_ratio']:.2f}",
                'Consistency': f"{result['consistency_score']:.1%}"
            })
        
        # Display comparison
        print("\n📊 Strategy Performance Comparison:")
        print("-" * 80)
        for data in comparison_data:
            print(f"{data['Symbol']:<12} | {data['Avg Return']:<10} | {data['Win Rate']:<8} | "
                  f"{data['Profit Factor']:<6} | {data['Max DD']:<8} | {data['Sharpe']:<6} | {data['Consistency']}")
        
        return results


def main():
    """Run advanced backtesting"""
    backtester = AdvancedBacktester(initial_capital=10000)
    
    # Test symbols
    symbols = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    
    print("🚀 Advanced Backtesting System")
    print("="*50)
    
    # Run comprehensive analysis
    for symbol in symbols:
        print(f"\n{'='*20} {symbol} {'='*20}")
        
        # Walk-forward analysis
        wf_result = backtester.run_backtest(symbol, walk_forward=True)
        
        # Monte Carlo simulation
        mc_result = backtester.monte_carlo_simulation(symbol, num_simulations=500)
    
    # Compare strategies
    backtester.compare_strategies(symbols)


if __name__ == "__main__":
    main()
