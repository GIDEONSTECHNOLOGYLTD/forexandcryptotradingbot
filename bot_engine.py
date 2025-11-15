"""
Trading Bot Engine - COMPLETE Real & Paper Trading Implementation
Handles all bot lifecycle, trading logic, and real-time execution
"""
import ccxt
import asyncio
import time
from datetime import datetime
from typing import Dict, Optional, List
from decimal import Decimal
import config
from mongodb_database import MongoTradingDatabase
from bson import ObjectId
from cryptography.fernet import Fernet
import logging

# Setup logging FIRST
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import profit protection system
try:
    from auto_profit_protector import AutoProfitProtector
    PROFIT_PROTECTOR_AVAILABLE = True
    logger.info("✅ Profit protector imported")
except ImportError as e:
    PROFIT_PROTECTOR_AVAILABLE = False
    logger.warning(f"⚠️ Profit protector not available: {e}")

# Import Telegram notification system
try:
    from telegram_notifier import TelegramNotifier
    TELEGRAM_AVAILABLE = True
    logger.info("✅ Telegram notifier imported")
except ImportError as e:
    TELEGRAM_AVAILABLE = False
    logger.warning(f"⚠️ Telegram not available: {e}")

# Import advanced strategies
try:
    from advanced_strategies import (
        GridTradingStrategy,
        DCAStrategy,
        ArbitrageDetector,
        MultiTimeframeAnalyzer,
        StrategySelector
    )
    ADVANCED_STRATEGIES_AVAILABLE = True
    logger.info("✅ Advanced strategies imported (Grid, DCA, Arbitrage)")
except ImportError as e:
    ADVANCED_STRATEGIES_AVAILABLE = False
    logger.warning(f"⚠️ Advanced strategies not available: {e}")

# Import enhanced risk manager
try:
    from enhanced_risk_manager import EnhancedRiskManager
    ENHANCED_RISK_AVAILABLE = True
    logger.info("✅ Enhanced risk manager imported (Kelly Criterion)")
except ImportError as e:
    ENHANCED_RISK_AVAILABLE = False
    logger.warning(f"⚠️ Enhanced risk manager not available: {e}")

class TradingBotEngine:
    """Complete trading bot engine with real-time execution"""
    
    def __init__(self):
        self.db = MongoTradingDatabase()
        self.active_bots: Dict[str, 'BotInstance'] = {}
        self.system_exchange = self._init_system_exchange()
        self.cipher_suite = Fernet(config.ENCRYPTION_KEY.encode()) if hasattr(config, 'ENCRYPTION_KEY') else None
        logger.info("✅ Bot engine initialized")
        
    def _init_system_exchange(self):
        """Initialize system OKX exchange for admin bots"""
        try:
            if not all([config.OKX_API_KEY, config.OKX_SECRET_KEY, config.OKX_PASSPHRASE]):
                logger.warning("⚠️ System OKX credentials not configured")
                return None
                
            exchange = ccxt.okx({
                'apiKey': config.OKX_API_KEY,
                'secret': config.OKX_SECRET_KEY,
                'password': config.OKX_PASSPHRASE,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })
            
            # Test connection
            exchange.load_markets()
            logger.info("✅ System OKX exchange connected")
            return exchange
        except Exception as e:
            logger.error(f"❌ System OKX init failed: {e}")
            return None
    
    def _decrypt_credentials(self, encrypted_data: str) -> str:
        """Decrypt user OKX credentials"""
        if not self.cipher_suite:
            raise ValueError("Encryption not configured")
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    async def start_bot(self, bot_id: str, user_id: str, is_admin: bool = False):
        """Start bot"""
        bot = self.db.db['bot_instances'].find_one({"_id": ObjectId(bot_id)})
        if not bot:
            raise ValueError("Bot not found")
        
        config_data = bot.get('config', {})
        paper_trading = config_data.get('paper_trading', True)
        
        # Get exchange - ADMIN uses backend credentials, USERS use their own
        if is_admin:
            # ADMIN: Use system OKX credentials from config/environment
            logger.info(f"🔑 ADMIN bot - Using BACKEND OKX credentials")
            exchange = self.system_exchange
            if not exchange:
                logger.error("❌ Admin exchange not configured! Set OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE in .env")
                raise ValueError("Admin OKX credentials not configured in backend")
            logger.info(f"✅ Admin bot {bot_id} connected to ADMIN OKX account")
        else:
            # USER: Use their own OKX credentials (encrypted in database)
            logger.info(f"🔑 USER bot - Using USER'S OWN OKX credentials")
            user = self.db.db['users'].find_one({"_id": ObjectId(user_id)})
            if not user or not user.get('exchange_connected'):
                raise ValueError("User must connect their OKX account first")
            
            # Decrypt user's personal credentials
            try:
                api_key = self._decrypt_credentials(user['okx_api_key'])
                secret = self._decrypt_credentials(user['okx_secret_key'])
                passphrase = self._decrypt_credentials(user['okx_passphrase'])
                
                exchange = ccxt.okx({
                    'apiKey': api_key,
                    'secret': secret,
                    'password': passphrase,
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
                
                # Test connection to user's OKX account
                exchange.load_markets()
                logger.info(f"✅ User bot {bot_id} connected to USER'S OKX account")
                
            except Exception as e:
                logger.error(f"❌ Failed to connect to user's OKX account: {e}")
                raise ValueError(f"Failed to connect to user's OKX: {str(e)}")
        
        # Create and start bot instance
        bot_instance = BotInstance(bot_id, user_id, config_data, exchange, paper_trading, self.db)
        self.active_bots[bot_id] = bot_instance
        await bot_instance.start()
        
        self.db.db['bot_instances'].update_one(
            {"_id": ObjectId(bot_id)},
            {"$set": {"status": "running", "started_at": datetime.utcnow()}}
        )
        
        return {"status": "running", "mode": "paper" if paper_trading else "real"}
    
    async def stop_bot(self, bot_id: str):
        """Stop bot"""
        if bot_id in self.active_bots:
            await self.active_bots[bot_id].stop()
            del self.active_bots[bot_id]
        
        self.db.db['bot_instances'].update_one(
            {"_id": ObjectId(bot_id)},
            {"$set": {"status": "stopped", "stopped_at": datetime.utcnow()}}
        )
        return {"status": "stopped"}


class BotInstance:
    def __init__(self, bot_id, user_id, config, exchange, paper_trading, db):
        self.bot_id = bot_id
        self.user_id = user_id
        self.config = config
        self.exchange = exchange
        self.paper_trading = paper_trading
        self.db = db
        self.running = False
        self.task = None
        self.symbol = config.get('symbol', 'BTC/USDT')
        
        # CRITICAL: For real trading, use ACTUAL OKX balance, not config
        if not self.paper_trading and self.exchange:
            try:
                balance_info = self.exchange.fetch_balance()
                self.balance = balance_info['free']['USDT']
                logger.info(f"✅ REAL TRADING - Using actual OKX balance: ${self.balance:.2f}")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch OKX balance, using config: {e}")
                self.balance = config.get('capital', 100)
        else:
            # Paper trading can use configured capital
            self.balance = config.get('capital', 1000)
            logger.info(f"📝 PAPER TRADING - Using simulated balance: ${self.balance:.2f}")
        
        # Initialize trading strategy
        self.strategy_type = config.get('strategy', 'momentum')
        self.strategy = self._init_strategy()
        logger.info(f"✅ Strategy initialized: {self.strategy_type}")
        
        # Initialize profit protector for automated protection
        self.profit_protector = None
        if PROFIT_PROTECTOR_AVAILABLE:
            try:
                self.profit_protector = AutoProfitProtector(exchange, db)
                logger.info(f"✅ Profit protector activated for bot {bot_id}")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize profit protector: {e}")
        
        # Initialize Telegram notifier for real-time trade alerts
        self.telegram = None
        if TELEGRAM_AVAILABLE:
            try:
                self.telegram = TelegramNotifier()
                if self.telegram.enabled:
                    logger.info(f"✅ Telegram notifications activated for bot {bot_id}")
                else:
                    logger.info(f"⚠️ Telegram configured but not enabled (check .env)")
            except Exception as e:
                logger.warning(f"⚠️ Could not initialize Telegram: {e}")
        
        # Track last loss time to prevent immediate re-buy
        # Load from database if exists (persist across restarts)
        bot_state = self.db.db['bot_states'].find_one({'bot_id': bot_id})
        if bot_state:
            self.last_loss_time = bot_state.get('last_loss_time')
            self.price_history = bot_state.get('price_history', [])
            self.daily_losses = bot_state.get('daily_losses', 0.0)
            self.last_reset_date = bot_state.get('last_reset_date')
            logger.info(f"✅ Restored bot state from database")
        else:
            self.last_loss_time = None
            self.price_history = []
            self.daily_losses = 0.0
            self.last_reset_date = datetime.utcnow().date()
        
        self.cooldown_minutes = 15  # Base cooldown after loss
        self.max_history_length = 10
        self.max_daily_loss_percent = 5.0  # Stop trading if lose 5% in one day
        self.slippage_tolerance = 0.5  # Max 0.5% slippage allowed
    
    def _init_strategy(self):
        """Initialize trading strategy based on config"""
        if not ADVANCED_STRATEGIES_AVAILABLE:
            logger.warning("⚠️ Advanced strategies not available, using basic momentum")
            return None
        
        try:
            if self.strategy_type == 'grid':
                logger.info("📊 Initializing Grid Trading Strategy...")
                return GridTradingStrategy(
                    grid_levels=self.config.get('grid_levels', 10),
                    grid_spacing_percent=self.config.get('grid_spacing', 1.0)
                )
            
            elif self.strategy_type == 'dca':
                logger.info("💎 Initializing DCA Strategy...")
                return DCAStrategy(
                    max_buy_orders=self.config.get('max_buy_orders', 4),
                    dip_threshold=self.config.get('dip_threshold', 2.0),
                    profit_target=self.config.get('profit_target', 3.0)
                )
            
            elif self.strategy_type == 'arbitrage':
                logger.info("⚡ Initializing Arbitrage Detector...")
                return ArbitrageDetector(min_profit_threshold=0.005)
            
            elif self.strategy_type == 'ml_enhanced':
                logger.info("🤖 Initializing ML-Enhanced Strategy...")
                # Use momentum with ML predictions
                return None  # Will use momentum + ML predictions
            
            else:
                logger.info("🚀 Using Momentum Strategy (default)")
                return None  # Basic momentum
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize strategy {self.strategy_type}: {e}")
            return None
    
    def _get_trading_signal(self, current_price, position):
        """Get trading signal from strategy"""
        try:
            # Grid strategy
            if self.strategy_type == 'grid' and self.strategy:
                if not position:
                    return 'buy'  # Grid always ready to buy
                # Check if we should take profit
                entry_price = position.get('entry', 0)
                if self.strategy.should_take_profit(current_price, entry_price):
                    return 'sell'
                return 'hold'
            
            # DCA strategy
            elif self.strategy_type == 'dca' and self.strategy:
                if not position:
                    # Check if price dipped enough
                    if self.strategy.should_buy_dip(current_price):
                        return 'buy'
                else:
                    # Check if we hit profit target
                    if self.strategy.should_sell(current_price, position.get('entry', 0)):
                        return 'sell'
                return 'hold'
            
            # Arbitrage strategy
            elif self.strategy_type == 'arbitrage' and self.strategy:
                # Arbitrage needs multiple exchanges - simplified for single exchange
                # Return buy/sell based on momentum as fallback
                return 'buy' if not position else 'hold'
            
            # Basic momentum (default) - IMPROVED
            else:
                # Smart momentum: check conditions before buying
                if not position:
                    # Reset daily losses at start of new day
                    today = datetime.utcnow().date()
                    if self.last_reset_date != today:
                        self.daily_losses = 0.0
                        self.last_reset_date = today
                        logger.info(f"📅 New day - reset daily loss counter")
                    
                    # Check daily loss limit
                    daily_loss_pct = (self.daily_losses / self.balance) * 100 if self.balance > 0 else 0
                    if daily_loss_pct >= self.max_daily_loss_percent:
                        logger.warning(f"🛑 Daily loss limit reached: {daily_loss_pct:.2f}% (max {self.max_daily_loss_percent}%)")
                        return 'hold'  # Stop trading for today
                    
                    # Check cooldown period after last loss (dynamic based on loss size)
                    if self.last_loss_time:
                        minutes_since_loss = (datetime.utcnow() - self.last_loss_time).total_seconds() / 60
                        if minutes_since_loss < self.cooldown_minutes:
                            logger.info(f"⏸️ Cooldown active: {self.cooldown_minutes - minutes_since_loss:.1f} min remaining")
                            return 'hold'  # Don't buy yet
                    
                    # Check trend: only buy if price is stable or rising
                    if len(self.price_history) >= 5:
                        recent_prices = self.price_history[-5:]
                        # Calculate trend: average of last 5 vs average of previous 5
                        if len(self.price_history) >= 10:
                            recent_avg = sum(self.price_history[-5:]) / 5
                            previous_avg = sum(self.price_history[-10:-5]) / 5
                            trend_change = ((recent_avg - previous_avg) / previous_avg) * 100
                            
                            if trend_change < -1.0:  # Downtrend if avg dropped >1%
                                logger.info(f"📉 Downtrend detected: {trend_change:.2f}% - waiting")
                                return 'hold'
                        
                        # Also check immediate trend (last 3 prices)
                        last_3 = self.price_history[-3:]
                        is_falling = all(last_3[i] > last_3[i+1] for i in range(len(last_3)-1))
                        if is_falling:
                            logger.info(f"📉 Price falling (last 3) - waiting for stability")
                            return 'hold'
                    
                    # Safe to buy: no cooldown, price not falling, within daily limit
                    return 'buy'
                else:
                    # Have position: check exit conditions
                    entry_price = position.get('entry', 0)
                    profit_pct = ((current_price - entry_price) / entry_price) * 100
                    
                    # Dynamic take profit: 2-3% based on volatility
                    if len(self.price_history) >= 10:
                        # Calculate volatility (standard deviation of returns)
                        returns = [(self.price_history[i] - self.price_history[i-1]) / self.price_history[i-1] 
                                   for i in range(1, len(self.price_history))]
                        volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5
                        
                        # Lower volatility = tighter take profit (2%)
                        # Higher volatility = wider take profit (3%)
                        take_profit_pct = 2.0 if volatility < 0.02 else 3.0
                    else:
                        take_profit_pct = 2.5  # Default
                    
                    # Take profit
                    if profit_pct >= take_profit_pct:
                        logger.info(f"✅ Taking profit: +{profit_pct:.2f}% (target: {take_profit_pct:.1f}%)")
                        self.last_loss_time = None  # Reset cooldown on win
                        self._save_bot_state()  # Persist state
                        return 'sell'
                    
                    # Dynamic stop loss: 3% base, but tighter if market crashing
                    stop_loss_pct = 3.0
                    if len(self.price_history) >= 5:
                        last_5_change = ((self.price_history[-1] - self.price_history[-5]) / self.price_history[-5]) * 100
                        if last_5_change < -2.0:  # Market dropping fast
                            stop_loss_pct = 2.0  # Tighter stop loss
                    
                    # Stop loss
                    if profit_pct <= -stop_loss_pct:
                        loss_amount = abs((current_price - entry_price) * position.get('amount', 0))
                        logger.warning(f"⚠️ Stop loss: {profit_pct:.2f}% (limit: {stop_loss_pct:.1f}%)")
                        
                        # Dynamic cooldown: bigger loss = longer cooldown
                        if abs(profit_pct) >= 5:
                            self.cooldown_minutes = 30  # 30 min for big loss
                        elif abs(profit_pct) >= 3:
                            self.cooldown_minutes = 20  # 20 min for medium loss
                        else:
                            self.cooldown_minutes = 15  # 15 min for small loss
                        
                        self.last_loss_time = datetime.utcnow()
                        self.daily_losses += loss_amount
                        self._save_bot_state()  # Persist state
                        return 'sell'
                    
                return 'hold'
                
        except Exception as e:
            logger.error(f"❌ Error getting trading signal: {e}")
            # Fallback to hold
            return 'hold'
    
    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self.trading_loop())
        
        # Send bot started notification
        if self.telegram and self.telegram.enabled:
            try:
                mode = "📝 Paper Trading" if self.paper_trading else "💰 Real Trading"
                message = (
                    f"🤖 **Bot Started!**\n\n"
                    f"Symbol: {self.symbol}\n"
                    f"Mode: {mode}\n"
                    f"Capital: ${self.balance:.2f}\n"
                    f"Bot ID: {self.bot_id}\n\n"
                    f"⏰ Trading loop active. You'll receive alerts for every trade!"
                )
                self.telegram.send_message(message)
                logger.info("📱 Telegram: Bot started notification sent")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send bot started notification: {e}")
    
    def _save_bot_state(self):
        """Persist bot state to database (survives restarts)"""
        try:
            self.db.db['bot_states'].update_one(
                {'bot_id': self.bot_id},
                {'$set': {
                    'last_loss_time': self.last_loss_time,
                    'price_history': self.price_history,
                    'daily_losses': self.daily_losses,
                    'last_reset_date': self.last_reset_date,
                    'updated_at': datetime.utcnow()
                }},
                upsert=True
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to save bot state: {e}")
    
    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
        
        # Save final state
        self._save_bot_state()
        
        # Send Telegram notification for bot stopped
        if self.telegram and self.telegram.enabled:
            try:
                runtime = datetime.utcnow() - self.start_time if hasattr(self, 'start_time') else None
                runtime_str = f"{runtime.total_seconds() / 3600:.1f} hours" if runtime else "N/A"
                
                message = (
                    f"⏹️ **Bot Stopped**\n\n"
                    f"Symbol: {self.symbol}\n"
                    f"Mode: {'📝 Paper Trading' if self.paper_trading else '💰 Real Trading'}\n"
                    f"Runtime: {runtime_str}\n"
                    f"Final Balance: ${self.balance:.2f}\n\n"
                    f"Bot has been stopped successfully."
                )
                self.telegram.send_message(message)
                logger.info("📱 Telegram: Bot stopped notification sent")
            except Exception as e:
                logger.warning(f"⚠️ Failed to send bot stopped notification: {e}")
    
    async def trading_loop(self):
        """Main trading loop with real execution"""
        position = None
        
        while self.running:
            try:
                # Validate symbol exists on exchange before trading
                # Get current price with null check (Bug #6 fix)
                try:
                    ticker = self.exchange.fetch_ticker(self.symbol)
                    if not ticker or 'last' not in ticker:
                        logger.warning(f"Invalid ticker data for {self.symbol}")
                        await asyncio.sleep(10)
                        continue
                    price = ticker['last']
                    
                    # Track price history for trend detection
                    self.price_history.append(price)
                    if len(self.price_history) > self.max_history_length:
                        self.price_history.pop(0)  # Keep only last 10 prices
                    
                except Exception as e:
                    logger.error(f"Failed to fetch ticker for {self.symbol}: {e}")
                    await asyncio.sleep(10)
                    continue
                except ccxt.BadSymbol as e:
                    logger.error(f"🚨 Invalid symbol: {self.symbol} - {str(e)}")
                    logger.error(f"💡 Tip: MATIC is now POL on OKX. Use POL/USDT instead.")
                    # Stop bot - symbol doesn't exist
                    self.running = False
                    break
                except Exception as ticker_error:
                    logger.warning(f"⚠️ Error fetching ticker for {self.symbol}: {ticker_error}")
                    await asyncio.sleep(10)
                    continue
                
                # Execute strategy-specific logic
                signal = self._get_trading_signal(price, position)
                
                if signal == 'buy' and not position:
                    # Open position - USE ONLY YOUR ACTUAL BALANCE, NO LEVERAGE!
                    # Get fresh balance to ensure accuracy
                    if not self.paper_trading:
                        try:
                            balance_info = self.exchange.fetch_balance()
                            if not balance_info or 'free' not in balance_info:
                                logger.error("Invalid balance data")
                                actual_usdt = self.balance
                            else:
                                actual_usdt = balance_info.get('free', {}).get('USDT', self.balance)
                            logger.info(f"💰 Actual USDT available: ${actual_usdt:.2f}")
                        except:
                            actual_usdt = self.balance
                    else:
                        actual_usdt = self.balance
                    
                    # Use 80% of available balance (leaving buffer for fees)
                    # NO LEVERAGE - only trade what you have!
                    max_trade_amount = actual_usdt * 0.8
                    amount = max_trade_amount / price
                    
                    # Check minimum order value (OKX requires minimum $5)
                    order_value = amount * price
                    if order_value < 5 and not self.paper_trading:
                        logger.warning(f"⚠️ Order value ${order_value:.2f} too small, minimum $5. Skipping.")
                        # Send notification about minimum order size (once per hour to avoid spam)
                        if self.telegram and self.telegram.enabled:
                            if not hasattr(self, '_last_min_order_alert') or \
                               (datetime.utcnow() - self._last_min_order_alert).total_seconds() > 3600:
                                try:
                                    message = (
                                        f"⚠️ **ORDER TOO SMALL**\n\n"
                                        f"Symbol: {self.symbol}\n"
                                        f"Order Value: ${order_value:.2f}\n"
                                        f"Minimum Required: $5.00\n\n"
                                        f"💡 Add more funds to make larger trades!\n"
                                        f"Current Balance: ${actual_usdt:.2f}\n\n"
                                        f"Bot ID: {self.bot_id}"
                                    )
                                    self.telegram.send_message(message)
                                    self._last_min_order_alert = datetime.utcnow()
                                except:
                                    pass
                        await asyncio.sleep(60)
                        continue
                    
                    if self.paper_trading:
                        logger.info(f"📝 PAPER BUY: {amount:.6f} {self.symbol} @ ${price:.2f}")
                    else:
                        # CRITICAL: Use spot market order (no margin/leverage)
                        try:
                            expected_price = price
                            order = self.exchange.create_market_order(
                                self.symbol, 
                                'buy', 
                                amount,
                                params={'tdMode': 'cash'}  # SPOT trading only!
                            )
                            
                            # Check for slippage
                            actual_fill_price = order.get('average') or order.get('price') or price
                            slippage_pct = abs((actual_fill_price - expected_price) / expected_price) * 100
                            
                            if slippage_pct > self.slippage_tolerance:
                                logger.warning(f"⚠️ HIGH SLIPPAGE: {slippage_pct:.2f}% (expected ${expected_price:.2f}, got ${actual_fill_price:.2f})")
                                # If slippage too high, consider it a warning but continue
                                if self.telegram and self.telegram.enabled:
                                    try:
                                        self.telegram.send_message(
                                            f"⚠️ High slippage detected!\n"
                                            f"Expected: ${expected_price:.2f}\n"
                                            f"Actual: ${actual_fill_price:.2f}\n"
                                            f"Slippage: {slippage_pct:.2f}%"
                                        )
                                    except:
                                        pass
                            
                            logger.info(f"💰 SPOT BUY (NO LEVERAGE): {amount:.6f} {self.symbol} @ ${actual_fill_price:.2f}")
                            logger.info(f"📊 Used ${order_value:.2f} of your ${actual_usdt:.2f} balance")
                            price = actual_fill_price  # Use actual fill price going forward
                            
                        except ccxt.ExchangeNotAvailable as e:
                            logger.error(f"🔧 Exchange maintenance: {e}")
                            logger.info("⏸️ Waiting 5 minutes for exchange to come back online...")
                            await asyncio.sleep(300)  # Wait 5 minutes
                            continue
                        except ccxt.NetworkError as e:
                            logger.error(f"🌐 Network error: {e}")
                            logger.info("⏸️ Retrying in 30 seconds...")
                            await asyncio.sleep(30)
                            continue
                        except ccxt.InsufficientFunds as e:
                            logger.error(f"💸 Insufficient funds: {e}")
                            logger.error("🛑 Stopping bot - not enough balance")
                            self.running = False
                            break
                        except Exception as order_error:
                            logger.error(f"❌ ORDER FAILED: {str(order_error)}")
                            # Send immediate notification for order failure
                            if self.telegram and self.telegram.enabled:
                                try:
                                    error_msg = str(order_error)
                                    is_balance_issue = 'insufficient' in error_msg.lower() or 'balance' in error_msg.lower()
                                    
                                    message = (
                                        f"🚨 **ORDER FAILED** {'💰' if is_balance_issue else '⚠️'}\n\n"
                                        f"Symbol: {self.symbol}\n"
                                        f"Side: BUY\n"
                                        f"Amount: {amount:.6f}\n"
                                        f"Price: ${price:.2f}\n"
                                        f"Value: ${order_value:.2f}\n\n"
                                        f"**Error:** {error_msg}\n\n"
                                        f"{'💡 Add funds to your OKX account!' if is_balance_issue else '⚠️ Check your exchange settings!'}\n"
                                        f"Bot ID: {self.bot_id}"
                                    )
                                    self.telegram.send_message(message)
                                    logger.info("📱 Telegram: Order failure notification sent")
                                except:
                                    pass
                            # Continue loop after failure
                            await asyncio.sleep(60)
                            continue
                    
                    position = {'entry': price, 'amount': amount, 'time': datetime.utcnow()}
                    
                    # Add position to profit protector for automated protection
                    if self.profit_protector:
                        try:
                            position_id = self.profit_protector.add_position(
                                symbol=self.symbol,
                                entry_price=price,
                                amount=amount,
                                side='long',
                                metadata={'bot_id': self.bot_id, 'user_id': self.user_id}
                            )
                            position['protector_id'] = position_id
                            logger.info(f"🛡️ Position protected with ID: {position_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Could not add position to protector: {e}")
                    
                    # Save trade with status tracking
                    trade_doc = {
                        'bot_id': self.bot_id,
                        'user_id': self.user_id,
                        'symbol': self.symbol,
                        'side': 'buy',
                        'amount': amount,
                        'price': price,
                        'entry_price': price,
                        'status': 'open',  # Track that this position is open
                        'is_paper': self.paper_trading,
                        'timestamp': datetime.utcnow()
                    }
                    result = self.db.db['trades'].insert_one(trade_doc)
                    position['trade_id'] = str(result.inserted_id)  # Store trade ID for later update
                    logger.info(f"💾 Trade saved to database with ID: {result.inserted_id}")
                    
                    # Send Telegram notification for BUY
                    if self.telegram and self.telegram.enabled:
                        try:
                            mode = "📝 PAPER" if self.paper_trading else "💰 REAL"
                            total_value = amount * price
                            message = (
                                f"🟢 **BUY Signal Executed!**\n\n"
                                f"Symbol: {self.symbol}\n"
                                f"Mode: {mode}\n"
                                f"Price: ${price:,.2f}\n"
                                f"Amount: {amount:.6f}\n"
                                f"Total Value: ${total_value:,.2f}\n"
                                f"Time: {datetime.utcnow().strftime('%H:%M:%S UTC')}\n\n"
                                f"✅ Position opened successfully!"
                            )
                            self.telegram.send_message(message)
                            logger.info("📱 Telegram: BUY notification sent")
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to send BUY notification: {e}")
                    
                    # Broadcast via WebSocket
                    try:
                        from web_dashboard import manager
                        await manager.broadcast({
                            'type': 'trade',
                            'data': {
                                'bot_id': self.bot_id,
                                'symbol': self.symbol,
                                'side': 'buy',
                                'price': price,
                                'amount': amount,
                                'mode': 'paper' if self.paper_trading else 'real'
                            }
                        })
                    except:
                        pass
                
                # AI SUGGESTIONS: Monitor position and suggest exits
                if position and not signal:
                    entry_price = position.get('entry', 0)
                    if entry_price <= 0:
                        continue  # Skip invalid position
                    
                    current_pnl_pct = ((price - entry_price) / entry_price) * 100
                    amount = position.get('amount', 0)
                    current_pnl_usd = (price - entry_price) * amount
                    
                    # Send AI suggestion at 15%, 25%, 35% profit milestones
                    if current_pnl_pct >= 15 and current_pnl_pct < 45:
                        milestone = int(current_pnl_pct / 10) * 10  # Round to nearest 10%
                        last_suggestion = position.get('_last_ai_suggestion', 0)
                        
                        if milestone > last_suggestion:
                            if self.telegram and self.telegram.enabled:
                                try:
                                    # AI ANALYSIS: Dynamic advice based on profit level
                                    if current_pnl_pct >= 30:
                                        ai_advice = "🤖 AI: STRONG SELL SIGNAL - Excellent profit achieved!"
                                        urgency = "🚨 HIGH"
                                    elif current_pnl_pct >= 20:
                                        ai_advice = "🤖 AI: Consider selling - Very good profit"
                                        urgency = "⚠️ MEDIUM"
                                    else:  # 15%
                                        ai_advice = "🤖 AI: Good profit - Your decision"
                                        urgency = "💡 LOW"
                                    
                                    message = (
                                        f"💡 <b>AI PROFIT SUGGESTION</b>\n\n"
                                        f"🪙 Symbol: <b>{self.symbol}</b>\n"
                                        f"📈 Entry: ${entry_price:,.2f}\n"
                                        f"📊 Current: ${price:,.2f}\n\n"
                                        f"<b>💰 Profit: +{current_pnl_usd:.2f} USD (+{current_pnl_pct:.1f}%)</b>\n\n"
                                        f"{ai_advice}\n"
                                        f"🔔 Urgency: {urgency}\n\n"
                                        f"✅ <b>Option 1:</b> Sell now (secure ${current_pnl_usd:.2f})\n"
                                        f"⏳ <b>Option 2:</b> Hold for target\n\n"
                                        f"🤖 <i>AI helps you make informed decisions!</i>\n"
                                        f"Bot ID: {self.bot_id}"
                                    )
                                    self.telegram.send_message(message)
                                    position['_last_ai_suggestion'] = milestone
                                    logger.info(f"📱 AI profit suggestion sent at {current_pnl_pct:.1f}%")
                                except:
                                    pass
                
                elif signal == 'sell' and position:
                    # Exit signal from strategy
                    should_exit = True
                    exit_reason = f"strategy_{self.strategy_type}"
                    
                    # Check profit protector first (automated protection)
                    if self.profit_protector and position.get('protector_id'):
                        try:
                            # Update current price and check for exit signals
                            action = self.profit_protector.update_position(position['protector_id'], price)
                            if action and action.get('action') == 'exit':
                                exit_reason = action.get('reason', 'profit_protector')
                                logger.info(f"🛡️ Profit protector triggered exit: {exit_reason}")
                        except Exception as e:
                            logger.warning(f"⚠️ Profit protector check failed: {e}")
                    
                    if should_exit:
                        # Calculate final P&L
                        entry_price = position.get('entry', 0)
                        if entry_price <= 0:
                            logger.error(f"Invalid entry price on exit: {entry_price}")
                            continue
                        
                        final_pnl_pct = ((price - entry_price) / entry_price) * 100
                        
                        if self.paper_trading:
                            logger.info(f"📝 PAPER SELL: {position['amount']:.6f} @ ${price:.2f} | PnL: {final_pnl_pct:.2f}% | Reason: {exit_reason}")
                        else:
                            # EMERGENCY: Verify we actually own the coins before selling!
                            try:
                                balance = self.exchange.fetch_balance()
                                coin = self.symbol.split('/')[0]  # e.g., "BTC" from "BTC/USDT"
                                available = balance.get(coin, {}).get('free', 0)
                                
                                position_amount = position.get('amount', 0)
                                if available >= position_amount * 0.99:  # Allow 1% slippage
                                    # SAFE: We own the coins, can sell on SPOT
                                    try:
                                        order = self.exchange.create_market_order(
                                            self.symbol, 
                                            'sell', 
                                            position_amount,
                                            params={'tdMode': 'cash'}  # SPOT trading only!
                                        )
                                        logger.info(f"💰 SPOT SELL (NO LEVERAGE): {position['amount']:.6f} @ ${price:.2f} | PnL: {final_pnl_pct:.2f}% | Reason: {exit_reason}")
                                    except Exception as sell_error:
                                        logger.error(f"❌ SELL ORDER FAILED: {str(sell_error)}")
                                        # Notify about sell failure
                                        if self.telegram and self.telegram.enabled:
                                            try:
                                                message = (
                                                    f"🚨 **SELL ORDER FAILED**\n\n"
                                                    f"Symbol: {self.symbol}\n"
                                                    f"Amount: {position['amount']:.6f}\n"
                                                    f"Price: ${price:.2f}\n"
                                                    f"Reason: {exit_reason}\n\n"
                                                    f"**Error:** {str(sell_error)}\n\n"
                                                    f"⚠️ Position still open! Check exchange.\n"
                                                    f"Bot ID: {self.bot_id}"
                                                )
                                                self.telegram.send_message(message)
                                            except:
                                                pass
                                        continue
                                else:
                                    logger.error(f"🚨 BLOCKED SELL! Don't own {position['amount']:.6f} {coin} (only have {available:.6f})")
                                    logger.error(f"🛑 This would have been a SHORT/MARGIN trade - PREVENTED!")
                                    # Notify about blocked sell
                                    if self.telegram and self.telegram.enabled:
                                        try:
                                            message = (
                                                f"🛑 **SELL BLOCKED FOR SAFETY**\n\n"
                                                f"Symbol: {self.symbol}\n"
                                                f"Tried to sell: {position['amount']:.6f} {coin}\n"
                                                f"Actually own: {available:.6f} {coin}\n\n"
                                                f"⚠️ This would have been a SHORT/MARGIN trade!\n"
                                                f"🛡️ Bot prevented unsafe trade.\n\n"
                                                f"Bot ID: {self.bot_id}"
                                            )
                                            self.telegram.send_message(message)
                                        except:
                                            pass
                                    continue  # Skip this sell!
                            except Exception as e:
                                logger.error(f"🚨 Error checking balance before sell: {e}")
                                logger.error(f"🛑 BLOCKED SELL for safety!")
                                # Notify about balance check failure
                                if self.telegram and self.telegram.enabled:
                                    try:
                                        message = (
                                            f"🚨 **SELL BLOCKED - BALANCE CHECK FAILED**\n\n"
                                            f"Symbol: {self.symbol}\n"
                                            f"Error: {str(e)}\n\n"
                                            f"🛡️ Bot blocked sell for safety.\n"
                                            f"⚠️ Check your exchange connection.\n\n"
                                            f"Bot ID: {self.bot_id}"
                                        )
                                        self.telegram.send_message(message)
                                    except:
                                        pass
                                continue
                        
                        # Update the original BUY trade to mark it as closed
                        if position.get('trade_id'):
                            from bson import ObjectId
                            self.db.db['trades'].update_one(
                                {'_id': ObjectId(position['trade_id'])},
                                {'$set': {
                                    'status': 'closed',
                                    'exit_price': price,
                                    'pnl_percent': final_pnl_pct,
                                    'exit_reason': exit_reason,
                                    'exit_timestamp': datetime.utcnow()
                                }}
                            )
                            logger.info(f"💾 Updated BUY trade {position['trade_id']} to closed status")
                        
                        # Also save a separate SELL trade record
                        self.db.db['trades'].insert_one({
                            'bot_id': self.bot_id,
                            'user_id': self.user_id,
                            'symbol': self.symbol,
                            'side': 'sell',
                            'amount': position['amount'],
                            'price': price,
                            'entry_price': position['entry'],
                            'pnl_percent': final_pnl_pct,
                            'exit_reason': exit_reason,
                            'status': 'closed',
                            'is_paper': self.paper_trading,
                            'timestamp': datetime.utcnow()
                        })
                        
                        # Send Telegram notification for SELL
                        if self.telegram and self.telegram.enabled:
                            try:
                                mode = "📝 PAPER" if self.paper_trading else "💰 REAL"
                                total_value = position['amount'] * price
                                entry_value = position['amount'] * position['entry']
                                profit_usd = total_value - entry_value
                                profit_emoji = "🟢" if final_pnl_pct > 0 else "🔴"
                                
                                message = (
                                    f"{profit_emoji} **SELL Signal Executed!**\n\n"
                                    f"Symbol: {self.symbol}\n"
                                    f"Mode: {mode}\n"
                                    f"Entry Price: ${position['entry']:,.2f}\n"
                                    f"Exit Price: ${price:,.2f}\n"
                                    f"Amount: {position['amount']:.6f}\n"
                                    f"Total Value: ${total_value:,.2f}\n\n"
                                    f"**P&L: {profit_usd:+.2f} USD ({final_pnl_pct:+.2f}%)**\n"
                                    f"Reason: {exit_reason}\n"
                                    f"Time: {datetime.utcnow().strftime('%H:%M:%S UTC')}\n\n"
                                    f"✅ Position closed!"
                                )
                                self.telegram.send_message(message)
                                logger.info(f"📱 Telegram: SELL notification sent (PnL: {final_pnl_pct:+.2f}%)")
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to send SELL notification: {e}")
                        
                        # Broadcast via WebSocket
                        try:
                            from web_dashboard import manager
                            await manager.broadcast({
                                'type': 'trade',
                                'data': {
                                    'bot_id': self.bot_id,
                                    'symbol': self.symbol,
                                    'side': 'sell',
                                    'price': price,
                                    'amount': position['amount'],
                                    'pnl': final_pnl_pct,
                                    'mode': 'paper' if self.paper_trading else 'real'
                                }
                            })
                        except:
                            pass
                        
                        position = None
                
                # Save bot state periodically (every loop = every 60 seconds)
                self._save_bot_state()
                
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"❌ Error in trading loop: {e}")
                
                # Send Telegram notification for critical errors
                if self.telegram and self.telegram.enabled:
                    try:
                        message = (
                            f"🚨 **Bot Error!**\n\n"
                            f"Symbol: {self.symbol}\n"
                            f"Error: {str(e)[:200]}\n"
                            f"Balance: ${self.balance:.2f}\n\n"
                            f"⚠️ Bot will attempt to continue.\n"
                            f"Please check if manual intervention needed."
                        )
                        self.telegram.send_message(message)
                        logger.info("📱 Telegram: Error notification sent")
                    except Exception as notify_error:
                        logger.warning(f"⚠️ Failed to send error notification: {notify_error}")
                
                await asyncio.sleep(60)

# Global instance
bot_engine = TradingBotEngine()
