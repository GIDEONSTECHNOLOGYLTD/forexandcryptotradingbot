"""
Backtesting Framework
Test trading strategies on historical data before risking real money
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
from colorama import Fore, Style
from tabulate import tabulate
import matplotlib.pyplot as plt
import config
from strategy import TradingStrategy
from risk_manager import RiskManager


class Backtester:
    def __init__(self, initial_capital=10000):
        """Initialize backtester"""
        self.initial_capital = initial_capital
        self.strategy = TradingStrategy()
        self.results = []
        self.equity_curve = []
        
    def fetch_historical_data(self, exchange, symbol, timeframe, days=90):
        """Fetch historical OHLCV data"""
        print(f"{Fore.CYAN}📥 Fetching {days} days of historical data for {symbol}...{Style.RESET_ALL}")
        
        try:
            # Calculate how many candles we need
            since = exchange.parse8601((datetime.now() - timedelta(days=days)).isoformat())
            
            all_ohlcv = []
            while True:
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
                if not ohlcv:
                    break
                    
                all_ohlcv.extend(ohlcv)
                since = ohlcv[-1][0] + 1  # Next timestamp
                
                if len(ohlcv) < 1000:
                    break
            
            # Convert to DataFrame
            df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            print(f"{Fore.GREEN}✅ Fetched {len(df)} candles{Style.RESET_ALL}")
            return df
            
        except Exception as e:
            print(f"{Fore.RED}❌ Error fetching data: {e}{Style.RESET_ALL}")
            return None
    
    def run_backtest(self, df, symbol):
        """Run backtest on historical data"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"🔬 Running Backtest for {symbol}")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        # Initialize
        risk_manager = RiskManager(self.initial_capital)
        trades = []
        equity = [self.initial_capital]
        
        # Add indicators
        df = self.strategy.add_indicators(df)
        
        # Simulate trading
        for i in range(len(df)):
            if i < 50:  # Need enough data for indicators
                continue
            
            current_data = df.iloc[:i+1]
            current_price = df.iloc[i]['close']
            current_time = df.index[i]
            
            # Check if we have open positions
            if symbol in risk_manager.open_positions:
                # Check for stop-loss or take-profit
                exit_reason = risk_manager.check_stop_loss_take_profit(symbol, current_price)
                
                if exit_reason:
                    trade_record = risk_manager.close_position(symbol, current_price)
                    if trade_record:
                        trade_record['exit_time'] = current_time
                        trades.append(trade_record)
                        equity.append(risk_manager.current_capital)
            else:
                # Generate signal
                signal, confidence = self.strategy.generate_signal(current_data)
                
                if signal and confidence >= 60:
                    # Check if we can trade
                    can_trade, reason = risk_manager.can_trade()
                    
                    if can_trade:
                        # Calculate position size
                        position_size = risk_manager.calculate_position_size(symbol, current_price)
                        
                        # Open position
                        position = risk_manager.open_position(symbol, signal, current_price, position_size)
                        position['entry_time'] = current_time
                        position['confidence'] = confidence
        
        # Close any remaining positions
        if symbol in risk_manager.open_positions:
            final_price = df.iloc[-1]['close']
            trade_record = risk_manager.close_position(symbol, final_price)
            if trade_record:
                trade_record['exit_time'] = df.index[-1]
                trades.append(trade_record)
        
        # Store results
        self.results = trades
        self.equity_curve = equity
        
        # Generate report
        return self.generate_report(risk_manager, df)
    
    def generate_report(self, risk_manager, df):
        """Generate comprehensive backtest report"""
        stats = risk_manager.get_statistics()
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"📊 BACKTEST RESULTS")
        print(f"{'='*70}{Style.RESET_ALL}\n")
        
        # Performance metrics
        print(f"{Fore.YELLOW}Performance Metrics:{Style.RESET_ALL}")
        print(f"Initial Capital: ${self.initial_capital:,.2f}")
        
        capital_color = Fore.GREEN if stats['total_pnl'] >= 0 else Fore.RED
        print(f"Final Capital: {capital_color}${stats['current_capital']:,.2f}{Style.RESET_ALL}")
        print(f"Total PnL: {capital_color}${stats['total_pnl']:,.2f} ({stats['total_pnl_percent']:.2f}%){Style.RESET_ALL}")
        
        # Trade statistics
        print(f"\n{Fore.YELLOW}Trade Statistics:{Style.RESET_ALL}")
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Winning Trades: {Fore.GREEN}{stats['winning_trades']}{Style.RESET_ALL}")
        print(f"Losing Trades: {Fore.RED}{stats['losing_trades']}{Style.RESET_ALL}")
        
        if stats['total_trades'] > 0:
            win_rate_color = Fore.GREEN if stats['win_rate'] >= 50 else Fore.RED
            print(f"Win Rate: {win_rate_color}{stats['win_rate']:.2f}%{Style.RESET_ALL}")
            print(f"Average Win: {Fore.GREEN}${stats['avg_win']:.2f}{Style.RESET_ALL}")
            print(f"Average Loss: {Fore.RED}${stats['avg_loss']:.2f}{Style.RESET_ALL}")
            
            pf_color = Fore.GREEN if stats['profit_factor'] >= 1.5 else Fore.RED
            print(f"Profit Factor: {pf_color}{stats['profit_factor']:.2f}{Style.RESET_ALL}")
        
        # Risk metrics
        print(f"\n{Fore.YELLOW}Risk Metrics:{Style.RESET_ALL}")
        
        if self.equity_curve:
            equity_array = np.array(self.equity_curve)
            peak = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - peak) / peak * 100
            max_drawdown = np.min(drawdown)
            
            dd_color = Fore.GREEN if max_drawdown > -20 else Fore.RED
            print(f"Max Drawdown: {dd_color}{max_drawdown:.2f}%{Style.RESET_ALL}")
        
        # Calculate Sharpe Ratio (simplified)
        if len(self.results) > 1:
            returns = [t['pnl_percent'] for t in self.results]
            sharpe = (np.mean(returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
            sharpe_color = Fore.GREEN if sharpe > 1 else Fore.RED
            print(f"Sharpe Ratio: {sharpe_color}{sharpe:.2f}{Style.RESET_ALL}")
        
        # Trade distribution
        if self.results:
            print(f"\n{Fore.YELLOW}Trade Distribution:{Style.RESET_ALL}")
            
            # Create table
            trade_data = []
            for i, trade in enumerate(self.results[-10:], 1):  # Last 10 trades
                pnl_color = Fore.GREEN if trade['pnl'] > 0 else Fore.RED
                trade_data.append([
                    i,
                    trade['side'].upper(),
                    f"${trade['entry_price']:.2f}",
                    f"${trade['exit_price']:.2f}",
                    f"{pnl_color}${trade['pnl']:.2f}{Style.RESET_ALL}",
                    f"{pnl_color}{trade['pnl_percent']:.2f}%{Style.RESET_ALL}"
                ])
            
            headers = ['#', 'Side', 'Entry', 'Exit', 'PnL', 'PnL %']
            print(tabulate(trade_data, headers=headers, tablefmt='simple'))
        
        print(f"\n{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        # Return summary
        return {
            'initial_capital': self.initial_capital,
            'final_capital': stats['current_capital'],
            'total_pnl': stats['total_pnl'],
            'total_pnl_percent': stats['total_pnl_percent'],
            'total_trades': stats['total_trades'],
            'win_rate': stats['win_rate'],
            'profit_factor': stats['profit_factor'],
            'max_drawdown': max_drawdown if self.equity_curve else 0,
            'sharpe_ratio': sharpe if len(self.results) > 1 else 0
        }
    
    def plot_equity_curve(self, save_path='backtest_equity_curve.png'):
        """Plot equity curve"""
        if not self.equity_curve:
            print(f"{Fore.YELLOW}No equity data to plot{Style.RESET_ALL}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.equity_curve, linewidth=2)
        plt.axhline(y=self.initial_capital, color='r', linestyle='--', label='Initial Capital')
        plt.title('Equity Curve', fontsize=16, fontweight='bold')
        plt.xlabel('Trade Number')
        plt.ylabel('Capital ($)')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        print(f"{Fore.GREEN}✅ Equity curve saved to {save_path}{Style.RESET_ALL}")
        plt.close()
    
    def export_results(self, filename='backtest_results.csv'):
        """Export backtest results to CSV"""
        if not self.results:
            print(f"{Fore.YELLOW}No results to export{Style.RESET_ALL}")
            return
        
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"{Fore.GREEN}✅ Results exported to {filename}{Style.RESET_ALL}")


def run_backtest_example():
    """Example backtest run"""
    print(f"{Fore.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                      BACKTESTING FRAMEWORK                         ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    # Initialize exchange
    exchange = ccxt.okx({
        'enableRateLimit': True,
    })
    
    # Initialize backtester
    backtester = Backtester(initial_capital=10000)
    
    # Fetch historical data
    symbol = 'BTC/USDT'
    timeframe = '1h'
    days = 90
    
    df = backtester.fetch_historical_data(exchange, symbol, timeframe, days)
    
    if df is not None:
        # Run backtest
        results = backtester.run_backtest(df, symbol)
        
        # Plot equity curve
        backtester.plot_equity_curve()
        
        # Export results
        backtester.export_results()
        
        # Recommendation
        print(f"\n{Fore.YELLOW}💡 Recommendation:{Style.RESET_ALL}")
        if results['win_rate'] >= 50 and results['profit_factor'] >= 1.5:
            print(f"{Fore.GREEN}✅ Strategy looks promising! Consider live testing.{Style.RESET_ALL}")
        elif results['win_rate'] >= 40 and results['profit_factor'] >= 1.2:
            print(f"{Fore.YELLOW}⚠️  Strategy is marginal. Optimize parameters.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Strategy needs improvement. Don't trade live yet.{Style.RESET_ALL}")


if __name__ == "__main__":
    run_backtest_example()
