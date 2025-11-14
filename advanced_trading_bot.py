"""
Advanced Trading Bot with OKX Integration
Features: Multi-strategy, Risk Management, Token Scanner, Paper Trading
"""
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from colorama import Fore, Style, init
from tabulate import tabulate

import config
from risk_manager import RiskManager
from token_scanner import TokenScanner
from strategy import TradingStrategy
from telegram_notifier import TelegramNotifier

# Database options: SQLite or MongoDB
try:
    from mongodb_database import MongoTradingDatabase
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False

try:
    from database import TradingDatabase
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

# Initialize colorama
init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdvancedTradingBot:
    def __init__(self, use_database=True, use_telegram=True, use_mongodb=None):
        """Initialize the advanced trading bot"""
        self.exchange = self._initialize_exchange()
        self.risk_manager = RiskManager(config.INITIAL_CAPITAL)
        self.token_scanner = TokenScanner(self.exchange)
        self.strategy = TradingStrategy()
        self.active_symbols = []
        self.last_scan_time = None
        
        # Initialize database (MongoDB or SQLite)
        # Use MongoDB by default if configured in config.py
        if use_mongodb is None:
            use_mongodb = config.USE_MONGODB
        
        if use_database:
            if use_mongodb and MONGODB_AVAILABLE:
                try:
                    self.db = MongoTradingDatabase()
                    self.db_type = "MongoDB"
                except:
                    print(f"{Fore.YELLOW}⚠️  MongoDB failed, falling back to SQLite{Style.RESET_ALL}")
                    self.db = TradingDatabase() if SQLITE_AVAILABLE else None
                    self.db_type = "SQLite"
            elif SQLITE_AVAILABLE:
                self.db = TradingDatabase()
                self.db_type = "SQLite"
            else:
                self.db = None
                self.db_type = None
        else:
            self.db = None
            self.db_type = None
        
        # Initialize Telegram notifications
        self.telegram = TelegramNotifier() if use_telegram else None
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🤖 Advanced Trading Bot Initialized")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        print(f"Exchange: {Fore.GREEN}OKX{Style.RESET_ALL}")
        print(f"Mode: {Fore.YELLOW}{'PAPER TRADING' if config.PAPER_TRADING else 'LIVE TRADING'}{Style.RESET_ALL}")
        print(f"Initial Capital: {Fore.GREEN}${config.INITIAL_CAPITAL:,.2f}{Style.RESET_ALL}")
        print(f"Timeframe: {Fore.CYAN}{config.TIMEFRAME}{Style.RESET_ALL}")
        print(f"Max Positions: {Fore.CYAN}{config.MAX_OPEN_POSITIONS}{Style.RESET_ALL}")
        
        # Show database type
        if self.db:
            db_status = f"{self.db_type} Enabled"
            db_color = Fore.GREEN
        else:
            db_status = "Disabled"
            db_color = Fore.YELLOW
        print(f"Database: {db_color}{db_status}{Style.RESET_ALL}")
        
        print(f"Telegram: {Fore.GREEN if self.telegram and self.telegram.enabled else Fore.YELLOW}{'Enabled' if self.telegram and self.telegram.enabled else 'Disabled'}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        # Send bot started notification
        if self.telegram and self.telegram.enabled:
            self.telegram.send_bot_started()
        
    def _initialize_exchange(self):
        """Initialize OKX exchange connection"""
        try:
            exchange = ccxt.okx({
                'apiKey': config.OKX_API_KEY,
                'secret': config.OKX_SECRET_KEY,
                'password': config.OKX_PASSPHRASE,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                }
            })
            
            # Test connection
            exchange.load_markets()
            logger.info("Successfully connected to OKX")
            
            return exchange
            
        except Exception as e:
            logger.error(f"Failed to initialize OKX exchange: {e}")
            print(f"{Fore.RED}❌ Failed to connect to OKX. Check your API credentials.{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}💡 Make sure you have set OKX_API_KEY, OKX_SECRET_KEY, and OKX_PASSPHRASE in .env{Style.RESET_ALL}")
            raise
    
    def fetch_ohlcv(self, symbol, limit=100):
        """Fetch OHLCV data for a symbol"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, config.TIMEFRAME, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            return None
    
    def scan_for_opportunities(self):
        """Scan markets for trading opportunities"""
        current_time = datetime.now()
        
        # Check if it's time to scan
        if self.last_scan_time:
            time_since_scan = (current_time - self.last_scan_time).total_seconds() / 60
            if time_since_scan < config.SCAN_INTERVAL_MINUTES:
                return
        
        opportunities = self.token_scanner.scan_markets()
        self.token_scanner.display_opportunities()
        
        # Update active symbols
        self.active_symbols = [opp['symbol'] for opp in opportunities[:5]]
        self.last_scan_time = current_time
    
    def analyze_symbol(self, symbol):
        """Analyze a symbol and generate trading signal"""
        try:
            # Fetch market data
            df = self.fetch_ohlcv(symbol, limit=100)
            if df is None or len(df) < 50:
                return None, 0, None
            
            # Add technical indicators
            df = self.strategy.add_indicators(df)
            
            # Generate signal
            signal, confidence = self.strategy.generate_signal(df)
            
            # FORCE BUY ONLY for spot trading with USDT balance
            # Cannot sell/short without owning the coins first!
            if signal == 'sell':
                signal = 'hold'  # Skip sell signals, we need USDT to buy first!
            
            # Get market condition
            market_condition = self.strategy.analyze_market_condition(df)
            
            return signal, confidence, market_condition
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None, 0, None
    
    def execute_trade(self, symbol, signal, confidence):
        """Execute a trade (paper or live)"""
        try:
            # Check if we can trade
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                logger.warning(f"Cannot trade: {reason}")
                return False
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Calculate position size
            position_size = self.risk_manager.calculate_position_size(symbol, current_price)
            
            if config.PAPER_TRADING:
                # Paper trading
                print(f"\n{Fore.YELLOW}📝 PAPER TRADE{Style.RESET_ALL}")
                print(f"Symbol: {Fore.CYAN}{symbol}{Style.RESET_ALL}")
                print(f"Signal: {Fore.GREEN if signal == 'buy' else Fore.RED}{signal.upper()}{Style.RESET_ALL}")
                print(f"Confidence: {Fore.CYAN}{confidence:.1f}%{Style.RESET_ALL}")
                print(f"Entry Price: {Fore.CYAN}${current_price:.4f}{Style.RESET_ALL}")
                print(f"Position Size: {Fore.CYAN}{position_size:.4f}{Style.RESET_ALL}")
                
                # Open position in risk manager
                position = self.risk_manager.open_position(symbol, signal, current_price, position_size)
                position['confidence'] = confidence
                position['entry_time'] = datetime.now()
                
                print(f"Stop Loss: {Fore.RED}${position['stop_loss']:.4f}{Style.RESET_ALL}")
                print(f"Take Profit: {Fore.GREEN}${position['take_profit']:.4f}{Style.RESET_ALL}")
                
                # Save to database
                if self.db:
                    self.db.save_trade(position)
                
                # Send Telegram notification
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_trade_alert(position)
                
                logger.info(f"Paper trade executed: {signal} {symbol} at ${current_price:.4f}")
                return True
                
            else:
                # Live trading - SPOT ONLY!
                logger.warning("Live trading is enabled!")
                
                if signal == 'buy':
                    # SPOT BUY with USDT - no margin/leverage!
                    order = self.exchange.create_market_buy_order(
                        symbol, 
                        position_size,
                        params={'tdMode': 'cash'}  # SPOT trading only!
                    )
                    logger.info(f"✅ SPOT BUY executed: {symbol} - {position_size} @ ${current_price}")
                else:
                    # Should never reach here with our fix, but just in case
                    logger.warning(f"⚠️ Skipping SELL signal for {symbol} - need to BUY first!")
                    return False
                
                logger.info(f"Live trade executed: {order}")
                
                # Open position in risk manager
                position = self.risk_manager.open_position(symbol, signal, current_price, position_size)
                position['confidence'] = confidence
                position['entry_time'] = datetime.now()
                
                # Save to database
                if self.db:
                    self.db.save_trade(position)
                
                # Send Telegram notification
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_trade_alert(position)
                
                return True
                
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return False
    
    def check_open_positions(self):
        """Check open positions for stop-loss or take-profit"""
        for symbol in list(self.risk_manager.open_positions.keys()):
            try:
                # Get current price
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Check if stop-loss or take-profit hit
                exit_reason = self.risk_manager.check_stop_loss_take_profit(symbol, current_price)
                
                if exit_reason:
                    # Close position
                    trade_record = self.risk_manager.close_position(symbol, current_price)
                    
                    if trade_record:
                        print(f"\n{Fore.YELLOW}🔔 Position Closed{Style.RESET_ALL}")
                        print(f"Symbol: {Fore.CYAN}{symbol}{Style.RESET_ALL}")
                        print(f"Reason: {Fore.YELLOW}{exit_reason.upper()}{Style.RESET_ALL}")
                        print(f"Entry: ${trade_record['entry_price']:.4f} → Exit: ${trade_record['exit_price']:.4f}")
                        
                        pnl_color = Fore.GREEN if trade_record['pnl'] > 0 else Fore.RED
                        print(f"PnL: {pnl_color}${trade_record['pnl']:.2f} ({trade_record['pnl_percent']:.2f}%){Style.RESET_ALL}")
                        
                        # Update database
                        if self.db:
                            trade_record['exit_time'] = datetime.now()
                            trade_record['exit_reason'] = exit_reason
                            self.db.update_trade(symbol, trade_record)
                        
                        # Send Telegram notification
                        if self.telegram and self.telegram.enabled:
                            trade_record['exit_reason'] = exit_reason
                            self.telegram.send_position_closed(trade_record)
                        
                        logger.info(f"Position closed: {symbol} - {exit_reason} - PnL: ${trade_record['pnl']:.2f}")
                        
            except Exception as e:
                logger.error(f"Error checking position for {symbol}: {e}")
    
    def display_statistics(self, send_telegram=False):
        """Display trading statistics"""
        stats = self.risk_manager.get_statistics()
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📊 Trading Statistics")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
        
        # Capital info
        capital_color = Fore.GREEN if stats['total_pnl'] >= 0 else Fore.RED
        print(f"Current Capital: {capital_color}${stats['current_capital']:,.2f}{Style.RESET_ALL}")
        print(f"Total PnL: {capital_color}${stats['total_pnl']:,.2f} ({stats['total_pnl_percent']:.2f}%){Style.RESET_ALL}")
        print(f"Daily PnL: ${stats['daily_pnl']:,.2f}")
        
        # Trade statistics
        print(f"\nTotal Trades: {stats['total_trades']}")
        print(f"Winning Trades: {Fore.GREEN}{stats['winning_trades']}{Style.RESET_ALL}")
        print(f"Losing Trades: {Fore.RED}{stats['losing_trades']}{Style.RESET_ALL}")
        
        if stats['total_trades'] > 0:
            win_rate_color = Fore.GREEN if stats['win_rate'] >= 50 else Fore.RED
            print(f"Win Rate: {win_rate_color}{stats['win_rate']:.1f}%{Style.RESET_ALL}")
            print(f"Avg Win: {Fore.GREEN}${stats['avg_win']:.2f}{Style.RESET_ALL}")
            print(f"Avg Loss: {Fore.RED}${stats['avg_loss']:.2f}{Style.RESET_ALL}")
            print(f"Profit Factor: {stats['profit_factor']:.2f}")
        
        print(f"\nOpen Positions: {stats['open_positions']}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        # Save to database
        if self.db:
            self.db.save_performance_snapshot(stats)
        
        # Send Telegram summary if requested
        if send_telegram and self.telegram and self.telegram.enabled:
            self.telegram.send_daily_summary(stats)
    
    def run(self):
        """Main trading loop"""
        print(f"{Fore.GREEN}🚀 Starting trading bot...{Style.RESET_ALL}\n")
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                print(f"\n{Fore.CYAN}{'─'*70}")
                print(f"Iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'─'*70}{Style.RESET_ALL}")
                
                # Scan for opportunities periodically
                self.scan_for_opportunities()
                
                # Check open positions
                self.check_open_positions()
                
                # Analyze active symbols
                for symbol in self.active_symbols:
                    # Skip if already have position
                    if symbol in self.risk_manager.open_positions:
                        continue
                    
                    signal, confidence, market_condition = self.analyze_symbol(symbol)
                    
                    if signal == 'buy' and confidence >= 60:  # Only BUY signals!
                        print(f"\n{Fore.GREEN}✅ BUY Signal detected for {symbol}{Style.RESET_ALL}")
                        print(f"Market Condition: {market_condition}")
                        self.execute_trade(symbol, signal, confidence)
                
                # Display statistics every 5 iterations
                if iteration % 5 == 0:
                    self.display_statistics()
                
                # Send daily summary at midnight
                if datetime.now().hour == 0 and datetime.now().minute < 2:
                    self.display_statistics(send_telegram=True)
                
                # Wait before next iteration
                print(f"\n{Fore.YELLOW}⏳ Waiting 60 seconds...{Style.RESET_ALL}")
                time.sleep(60)
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}🛑 Stopping trading bot...{Style.RESET_ALL}")
            self.display_statistics()
            
            # Send bot stopped notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_bot_stopped()
            
            # Close database
            if self.db:
                self.db.close()
            
            print(f"{Fore.GREEN}✅ Bot stopped successfully{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"Critical error in main loop: {e}")
            print(f"{Fore.RED}❌ Critical error: {e}{Style.RESET_ALL}")
            
            # Send error notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_error_alert(str(e))
            
            # Close database
            if self.db:
                self.db.close()
            
            raise


def main():
    """Main entry point"""
    print(f"{Fore.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                   ADVANCED TRADING BOT v2.0                        ║")
    print("║                    OKX Multi-Strategy System                       ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    # Safety warning
    if not config.PAPER_TRADING:
        print(f"{Fore.RED}{'='*70}")
        print(f"⚠️  WARNING: LIVE TRADING MODE IS ENABLED!")
        print(f"{'='*70}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Auto-starting in LIVE trading mode...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💰 Real money will be used!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}📊 Max positions: {config.MAX_OPEN_POSITIONS}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*70}{Style.RESET_ALL}")
        # No input() on server - auto-continue!
    
    # Check API credentials
    if not config.OKX_API_KEY or not config.OKX_SECRET_KEY:
        print(f"{Fore.RED}❌ Error: OKX API credentials not found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please set OKX_API_KEY, OKX_SECRET_KEY, and OKX_PASSPHRASE in your .env file{Style.RESET_ALL}")
        return
    
    # Initialize and run bot
    bot = AdvancedTradingBot()
    bot.run()


if __name__ == "__main__":
    main()
