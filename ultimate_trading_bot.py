#!/usr/bin/env python3
"""
Ultimate AI-Powered Trading Bot
Combines advanced ML strategies, dynamic risk management, and sentiment analysis
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
from ai_strategy import AITradingStrategy
from advanced_risk_manager import AdvancedRiskManager
from token_scanner import TokenScanner
from telegram_notifier import TelegramNotifier

# Database options
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


class UltimateTradingBot:
    def __init__(self, use_database=True, use_telegram=True, use_mongodb=None):
        """Initialize the ultimate AI-powered trading bot"""
        self.exchange = self._initialize_exchange()
        self.risk_manager = AdvancedRiskManager(config.INITIAL_CAPITAL)
        self.strategy = AITradingStrategy()
        self.token_scanner = TokenScanner(self.exchange)
        self.active_symbols = []
        self.last_scan_time = None
        self.performance_tracker = []
        
        # Initialize database
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
        
        # Initialize Telegram
        self.telegram = TelegramNotifier() if use_telegram else None
        
        self._display_startup_info()
        
        # Send startup notification
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
                'options': {'defaultType': 'spot'}
            })
            
            exchange.load_markets()
            logger.info("Successfully connected to OKX")
            return exchange
            
        except Exception as e:
            logger.error(f"Failed to initialize OKX exchange: {e}")
            print(f"{Fore.RED}❌ Failed to connect to OKX. Check your API credentials.{Style.RESET_ALL}")
            raise
    
    def _display_startup_info(self):
        """Display startup information"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}🤖 ULTIMATE AI-POWERED TRADING BOT v3.0")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"🔥 Features: AI/ML Strategies, Dynamic Risk Management, Sentiment Analysis")
        print(f"Exchange: {Fore.GREEN}OKX{Style.RESET_ALL}")
        print(f"Mode: {Fore.YELLOW}{'PAPER TRADING' if config.PAPER_TRADING else 'LIVE TRADING'}{Style.RESET_ALL}")
        print(f"Initial Capital: {Fore.GREEN}${config.INITIAL_CAPITAL:,.2f}{Style.RESET_ALL}")
        print(f"Database: {Fore.GREEN if self.db else Fore.YELLOW}{self.db_type or 'Disabled'}{Style.RESET_ALL}")
        print(f"Telegram: {Fore.GREEN if self.telegram and self.telegram.enabled else Fore.YELLOW}{'Enabled' if self.telegram and self.telegram.enabled else 'Disabled'}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    def fetch_ohlcv(self, symbol, limit=200):
        """Fetch OHLCV data for analysis"""
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
        """Enhanced market scanning with AI analysis"""
        current_time = datetime.now()
        
        if self.last_scan_time:
            time_since_scan = (current_time - self.last_scan_time).total_seconds() / 60
            if time_since_scan < config.SCAN_INTERVAL_MINUTES:
                return
        
        print(f"\n{Fore.CYAN}🔍 Scanning markets for AI-powered opportunities...{Style.RESET_ALL}")
        
        opportunities = self.token_scanner.scan_markets()
        
        # Enhanced opportunity analysis
        enhanced_opportunities = []
        for opp in opportunities[:10]:  # Analyze top 10
            symbol = opp['symbol']
            df = self.fetch_ohlcv(symbol, limit=200)
            
            if df is not None and len(df) >= 100:
                signal, confidence, context = self.strategy.generate_advanced_signal(df, symbol)
                
                if signal and confidence >= 60:
                    enhanced_opp = {
                        **opp,
                        'ai_signal': signal,
                        'ai_confidence': confidence,
                        'market_regime': context.get('market_condition', 'unknown'),
                        'ml_prediction': context.get('ml_prediction', 0),
                        'sentiment': context.get('sentiment', 0.5)
                    }
                    enhanced_opportunities.append(enhanced_opp)
        
        # Sort by AI confidence
        enhanced_opportunities.sort(key=lambda x: x['ai_confidence'], reverse=True)
        
        self.active_symbols = [opp['symbol'] for opp in enhanced_opportunities[:5]]
        self.last_scan_time = current_time
        
        if enhanced_opportunities:
            self._display_opportunities(enhanced_opportunities[:5])
    
    def _display_opportunities(self, opportunities):
        """Display enhanced opportunities"""
        print(f"\n{Fore.GREEN}✨ AI-Enhanced Opportunities:{Style.RESET_ALL}")
        
        headers = ['Symbol', 'Signal', 'Confidence', 'Sentiment', 'ML Pred', 'Regime']
        rows = []
        
        for opp in opportunities:
            rows.append([
                opp['symbol'],
                f"{Fore.GREEN if opp['ai_signal'] == 'buy' else Fore.RED}{opp['ai_signal'].upper()}{Style.RESET_ALL}",
                f"{opp['ai_confidence']:.1f}%",
                f"{opp['sentiment']:.2f}",
                f"{opp['ml_prediction']:.3f}",
                opp['market_regime']
            ])
        
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    def analyze_symbol_advanced(self, symbol):
        """Advanced symbol analysis with AI"""
        try:
            df = self.fetch_ohlcv(symbol, limit=200)
            if df is None or len(df) < 100:
                return None, 0, None
            
            # Generate AI signal
            signal, confidence, context = self.strategy.generate_advanced_signal(df, symbol)
            
            return signal, confidence, context
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None, 0, None
    
    def execute_advanced_trade(self, symbol, signal, confidence, context):
        """Execute trade with advanced risk management"""
        try:
            # Portfolio risk check
            can_trade_portfolio, portfolio_reason = self.risk_manager.check_portfolio_risk_limits()
            if not can_trade_portfolio:
                logger.warning(f"Portfolio risk limit: {portfolio_reason}")
                return False
            
            # Basic risk check
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                logger.warning(f"Cannot trade: {reason}")
                return False
            
            # Get current price
            ticker = self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Calculate advanced position sizing
            volatility = context.get('volatility', 0.02)
            correlation_risk = self.risk_manager.calculate_portfolio_correlation_risk(
                symbol, list(self.risk_manager.open_positions.keys())
            )
            
            position_size, risk_percent = self.risk_manager.calculate_dynamic_position_size(
                symbol, current_price, confidence, volatility, correlation_risk
            )
            
            # Calculate dynamic stops
            stop_loss, stop_percent = self.risk_manager.calculate_dynamic_stop_loss(
                current_price, volatility, confidence, signal
            )
            take_profit, tp_percent = self.risk_manager.calculate_dynamic_take_profit(
                current_price, volatility, confidence, signal
            )
            
            if config.PAPER_TRADING:
                self._execute_paper_trade(symbol, signal, current_price, position_size, 
                                        confidence, context, stop_loss, take_profit, 
                                        risk_percent, stop_percent, tp_percent)
            else:
                self._execute_live_trade(symbol, signal, current_price, position_size)
            
            return True
            
        except Exception as e:
            logger.error(f"Error executing trade for {symbol}: {e}")
            return False
    
    def _execute_paper_trade(self, symbol, signal, current_price, position_size, 
                           confidence, context, stop_loss, take_profit, 
                           risk_percent, stop_percent, tp_percent):
        """Execute paper trade with detailed logging"""
        print(f"\n{Fore.YELLOW}📝 ADVANCED PAPER TRADE{Style.RESET_ALL}")
        print(f"Symbol: {Fore.CYAN}{symbol}{Style.RESET_ALL}")
        print(f"AI Signal: {Fore.GREEN if signal == 'buy' else Fore.RED}{signal.upper()}{Style.RESET_ALL}")
        print(f"Confidence: {Fore.CYAN}{confidence:.1f}%{Style.RESET_ALL}")
        print(f"Entry Price: {Fore.CYAN}${current_price:.4f}{Style.RESET_ALL}")
        print(f"Position Size: {Fore.CYAN}{position_size:.4f}{Style.RESET_ALL}")
        print(f"Risk %: {Fore.YELLOW}{risk_percent:.2%}{Style.RESET_ALL}")
        print(f"Stop Loss: {Fore.RED}${stop_loss:.4f} ({stop_percent:.1%}){Style.RESET_ALL}")
        print(f"Take Profit: {Fore.GREEN}${take_profit:.4f} ({tp_percent:.1%}){Style.RESET_ALL}")
        print(f"Market Regime: {Fore.MAGENTA}{context.get('market_condition', 'unknown')}{Style.RESET_ALL}")
        print(f"ML Prediction: {Fore.CYAN}{context.get('ml_prediction', 0):.3f}{Style.RESET_ALL}")
        print(f"Sentiment: {Fore.CYAN}{context.get('sentiment', 0.5):.2f}{Style.RESET_ALL}")
        
        # Open position
        position = self.risk_manager.open_position(symbol, signal, current_price, position_size)
        position.update({
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'confidence': confidence,
            'entry_time': datetime.now(),
            'context': context,
            'use_trailing_stop': True,
            'risk_percent': risk_percent
        })
        
        # Save to database
        if self.db:
            self.db.save_trade(position)
        
        # Send notification
        if self.telegram and self.telegram.enabled:
            self.telegram.send_trade_alert(position)
        
        logger.info(f"Advanced paper trade executed: {signal} {symbol} at ${current_price:.4f}")
    
    def _execute_live_trade(self, symbol, signal, current_price, position_size):
        """Execute live trade (use with extreme caution)"""
        logger.warning("LIVE TRADING ENABLED!")
        
        if signal == 'buy':
            order = self.exchange.create_market_buy_order(symbol, position_size)
        else:
            order = self.exchange.create_market_sell_order(symbol, position_size)
        
        logger.info(f"Live trade executed: {order}")
    
    def check_positions_advanced(self):
        """Advanced position monitoring with trailing stops"""
        for symbol in list(self.risk_manager.open_positions.keys()):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Get position for validation
                position = self.risk_manager.open_positions.get(symbol)
                if not position:
                    logger.warning(f"⚠️ Position for {symbol} not found, skipping...")
                    continue
                
                # Update position tracking
                self.risk_manager.update_position_tracking(symbol, current_price)
                
                # Check exit conditions
                exit_reason = self.risk_manager.check_stop_loss_take_profit(symbol, current_price)
                
                if exit_reason:
                    # Verify position still exists and has amount
                    if 'amount' not in position or position['amount'] <= 0:
                        logger.error(f"❌ Invalid position data for {symbol}, cannot execute sell")
                        continue
                    
                    # 🔴 EXECUTE ACTUAL SELL ORDER ON EXCHANGE (if not paper trading)
                    sell_order_success = True
                    if not config.PAPER_TRADING:
                        try:
                            # Execute market sell order to close position
                            sell_order = self.exchange.create_market_sell_order(
                                symbol,
                                position['amount'],
                                params={'tdMode': 'cash'}  # SPOT trading only
                            )
                            logger.info(f"✅ SELL order executed on exchange: {symbol} - {position['amount']} @ ${current_price:.4f}")
                            print(f"{Fore.GREEN}✅ Sell order executed on OKX!{Style.RESET_ALL}")
                        except Exception as e:
                            logger.error(f"❌ Failed to execute sell order for {symbol}: {e}")
                            print(f"{Fore.RED}❌ Failed to close position on exchange: {e}{Style.RESET_ALL}")
                            sell_order_success = False
                            
                            # Send alert about failed sell
                            if self.telegram and self.telegram.enabled:
                                self.telegram.send_custom_alert(
                                    "⚠️ SELL ORDER FAILED",
                                    f"Failed to close {symbol} on exchange!\n\n"
                                    f"Reason: {exit_reason}\n"
                                    f"Price: ${current_price:.4f}\n"
                                    f"Amount: {position['amount']}\n\n"
                                    f"Error: {str(e)}\n\n"
                                    f"⚠️ Check your exchange manually!"
                                )
                            
                            # Skip internal state update if exchange order failed
                            continue
                    else:
                        logger.info(f"📝 Paper trading - simulated close for {symbol}")
                    
                    # Close position in internal state (only if paper trading OR sell succeeded)
                    if sell_order_success or config.PAPER_TRADING:
                        trade_record = self.risk_manager.close_position(symbol, current_price)
                    else:
                        logger.error(f"❌ Skipping internal close for {symbol} - exchange order failed")
                        continue
                    
                    if trade_record:
                        self._display_position_closed(trade_record, exit_reason)
                        
                        # Update database
                        if self.db:
                            trade_record['exit_time'] = datetime.now()
                            trade_record['exit_reason'] = exit_reason
                            self.db.update_trade(symbol, trade_record)
                        
                        # Send notification
                        if self.telegram and self.telegram.enabled:
                            trade_record['exit_reason'] = exit_reason
                            self.telegram.send_position_closed(trade_record)
                        
                        logger.info(f"Position closed: {symbol} - {exit_reason} - PnL: ${trade_record['pnl']:.2f}")
                        
            except Exception as e:
                logger.error(f"Error checking position for {symbol}: {e}")
    
    def _display_position_closed(self, trade_record, exit_reason):
        """Display position closure information"""
        print(f"\n{Fore.YELLOW}🔔 POSITION CLOSED{Style.RESET_ALL}")
        print(f"Symbol: {Fore.CYAN}{trade_record['symbol']}{Style.RESET_ALL}")
        print(f"Reason: {Fore.YELLOW}{exit_reason.upper()}{Style.RESET_ALL}")
        print(f"Entry: ${trade_record['entry_price']:.4f} → Exit: ${trade_record['exit_price']:.4f}")
        
        pnl_color = Fore.GREEN if trade_record['pnl'] > 0 else Fore.RED
        print(f"PnL: {pnl_color}${trade_record['pnl']:.2f} ({trade_record['pnl_percent']:.2f}%){Style.RESET_ALL}")
        
        if 'confidence' in trade_record:
            print(f"Original Confidence: {trade_record['confidence']:.1f}%")
    
    def display_advanced_statistics(self, send_telegram=False):
        """Display comprehensive trading statistics"""
        stats = self.risk_manager.get_advanced_statistics()
        
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}📊 ADVANCED TRADING STATISTICS")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
        # Capital info
        capital_color = Fore.GREEN if stats['total_pnl'] >= 0 else Fore.RED
        print(f"Current Capital: {capital_color}${stats['current_capital']:,.2f}{Style.RESET_ALL}")
        print(f"Total PnL: {capital_color}${stats['total_pnl']:,.2f} ({stats['total_pnl_percent']:.2f}%){Style.RESET_ALL}")
        print(f"Daily PnL: ${stats['daily_pnl']:,.2f}")
        
        # Trade statistics
        print(f"\n📈 Trade Performance:")
        print(f"Total Trades: {stats['total_trades']}")
        print(f"Win Rate: {Fore.GREEN if stats['win_rate'] >= 50 else Fore.RED}{stats['win_rate']:.1f}%{Style.RESET_ALL}")
        print(f"Profit Factor: {stats['profit_factor']:.2f}")
        
        # Advanced metrics
        print(f"\n🎯 Advanced Metrics:")
        print(f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}")
        print(f"Sortino Ratio: {stats['sortino_ratio']:.2f}")
        print(f"Calmar Ratio: {stats['calmar_ratio']:.2f}")
        print(f"Max Drawdown: {Fore.RED}{stats['max_drawdown']:.2%}{Style.RESET_ALL}")
        print(f"Current Drawdown: {stats['current_drawdown']:.2%}")
        print(f"VaR (95%): {stats['var_95']:.2%}")
        print(f"Expected Shortfall: {stats['expected_shortfall']:.2%}")
        
        # Portfolio metrics
        print(f"\n💼 Portfolio Metrics:")
        print(f"Open Positions: {stats['open_positions']}")
        print(f"Portfolio Correlation Risk: {stats['portfolio_correlation_risk']:.2f}")
        print(f"Optimal Kelly %: {stats['kelly_fraction']:.1%}")
        print(f"Risk-Adjusted Return: {stats['risk_adjusted_return']:.2f}")
        
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        # Save performance snapshot
        if self.db:
            self.db.save_performance_snapshot(stats)
        
        # Send Telegram summary
        if send_telegram and self.telegram and self.telegram.enabled:
            self.telegram.send_daily_summary(stats)
    
    def run(self):
        """Main enhanced trading loop"""
        print(f"{Fore.GREEN}🚀 Starting Ultimate AI Trading Bot...{Style.RESET_ALL}\n")
        
        iteration = 0
        
        try:
            while True:
                iteration += 1
                print(f"\n{Fore.CYAN}{'─'*80}")
                print(f"🤖 AI Trading Iteration #{iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'─'*80}{Style.RESET_ALL}")
                
                # Enhanced market scanning
                self.scan_for_opportunities()
                
                # Advanced position monitoring
                self.check_positions_advanced()
                
                # Analyze active symbols with AI
                for symbol in self.active_symbols:
                    if symbol in self.risk_manager.open_positions:
                        continue
                    
                    signal, confidence, context = self.analyze_symbol_advanced(symbol)
                    
                    if signal and confidence >= 65:
                        print(f"\n{Fore.GREEN}✅ AI Signal detected for {symbol}{Style.RESET_ALL}")
                        print(f"Market Regime: {context.get('market_condition', 'unknown')}")
                        print(f"ML Prediction: {context.get('ml_prediction', 0):.3f}")
                        print(f"Sentiment: {context.get('sentiment', 0.5):.2f}")
                        
                        self.execute_advanced_trade(symbol, signal, confidence, context)
                
                # Display statistics periodically
                if iteration % 5 == 0:
                    self.display_advanced_statistics()
                
                # Send daily summary
                if datetime.now().hour == 0 and datetime.now().minute < 2:
                    self.display_advanced_statistics(send_telegram=True)
                
                # Wait before next iteration
                print(f"\n{Fore.YELLOW}⏳ Waiting 60 seconds for next AI analysis...{Style.RESET_ALL}")
                time.sleep(60)
                
        except KeyboardInterrupt:
            self._handle_shutdown()
        except Exception as e:
            self._handle_error(e)
    
    def _handle_shutdown(self):
        """Handle graceful shutdown"""
        print(f"\n\n{Fore.YELLOW}🛑 Stopping Ultimate AI Trading Bot...{Style.RESET_ALL}")
        self.display_advanced_statistics()
        
        if self.telegram and self.telegram.enabled:
            self.telegram.send_bot_stopped()
        
        if self.db:
            self.db.close()
        
        print(f"{Fore.GREEN}✅ Ultimate AI Bot stopped successfully{Style.RESET_ALL}")
    
    def _handle_error(self, error):
        """Handle critical errors"""
        logger.error(f"Critical error in main loop: {error}")
        print(f"{Fore.RED}❌ Critical error: {error}{Style.RESET_ALL}")
        
        if self.telegram and self.telegram.enabled:
            self.telegram.send_error_alert(str(error))
        
        if self.db:
            self.db.close()
        
        raise


def main():
    """Main entry point"""
    print(f"{Fore.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                 ULTIMATE AI TRADING BOT v3.0                      ║")
    print("║           Advanced ML • Dynamic Risk • Sentiment Analysis          ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}")
    
    # Safety warning
    if not config.PAPER_TRADING:
        print(f"{Fore.RED}{'='*70}")
        print(f"⚠️  WARNING: LIVE TRADING MODE IS ENABLED!")
        print(f"{'='*70}{Style.RESET_ALL}")
        response = input(f"{Fore.YELLOW}Are you sure you want to continue? (yes/no): {Style.RESET_ALL}")
        if response.lower() != 'yes':
            print(f"{Fore.GREEN}Exiting...{Style.RESET_ALL}")
            return
    
    # Check API credentials
    if not config.OKX_API_KEY or not config.OKX_SECRET_KEY:
        print(f"{Fore.RED}❌ Error: OKX API credentials not found!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please set OKX_API_KEY, OKX_SECRET_KEY, and OKX_PASSPHRASE in your .env file{Style.RESET_ALL}")
        return
    
    # Initialize and run ultimate bot
    bot = UltimateTradingBot()
    bot.run()


if __name__ == "__main__":
    main()
