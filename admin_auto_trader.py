"""
ADMIN AUTO-TRADER - Fully Automated Trading While You Sleep
Grows your capital automatically with full Telegram notifications
"""
import ccxt
import time
import logging
from datetime import datetime
from mongodb_database import MongoTradingDatabase
from new_listing_bot import NewListingBot
from auto_profit_protector import AutoProfitProtector
from telegram_notifier import TelegramNotifier
import config

# Import Advanced AI Engine for smart trading decisions
try:
    from advanced_ai_engine import AdvancedAIEngine
    ADVANCED_AI_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Advanced AI Engine imported")
except ImportError as e:
    ADVANCED_AI_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Advanced AI not available: {e}")

logging.basicConfig(level=logging.INFO)

class AdminAutoTrader:
    """
    Fully automated trading system for admin
    Runs 24/7, grows capital automatically
    """
    
    def __init__(self):
        self.db = MongoTradingDatabase()
        
        # Initialize OKX with admin credentials
        self.exchange = ccxt.okx({
            'apiKey': config.OKX_API_KEY,
            'secret': config.OKX_SECRET_KEY,
            'password': config.OKX_PASSPHRASE,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        # Initialize bots with configuration from config.py
        new_listing_config = {
            'check_interval': config.NEW_LISTING_CHECK_INTERVAL,
            'buy_amount_usdt': config.NEW_LISTING_BUY_AMOUNT,
            'take_profit_percent': config.NEW_LISTING_TAKE_PROFIT,
            'stop_loss_percent': config.NEW_LISTING_STOP_LOSS,
            'max_hold_time': config.NEW_LISTING_MAX_HOLD
        }
        self.new_listing_bot = NewListingBot(self.exchange, self.db, config=new_listing_config)
        
        # Initialize Telegram notifications FIRST
        self.telegram = TelegramNotifier()
        
        # Pass telegram to profit protector for comprehensive notifications
        self.profit_protector = AutoProfitProtector(self.exchange, self.db, telegram=self.telegram)
        
        # Initialize Advanced AI Engine for smart trading
        if ADVANCED_AI_AVAILABLE:
            self.ai_engine = AdvancedAIEngine(self.exchange)
            logger.info("✅ Advanced AI Engine initialized for admin trader")
        else:
            self.ai_engine = None
            logger.warning("⚠️ Trading without Advanced AI - using basic logic")
        
        # Trading settings - dynamically fetched from actual balance
        self.capital = self.get_current_balance()  # Get real balance instead of hardcoded
        self.min_trade_size = config.ADMIN_MIN_TRADE_SIZE
        self.max_trade_size = config.ADMIN_MAX_TRADE_SIZE
        self.target_profit_per_trade = config.ADMIN_TARGET_PROFIT
        self.max_loss_per_trade = config.ADMIN_STOP_LOSS
        self.momentum_min_balance = config.ADMIN_MOMENTUM_MIN_BALANCE
        
        # Small profit accumulation strategy
        self.small_profit_mode = config.ADMIN_SMALL_PROFIT_MODE
        self.small_win_target = config.ADMIN_SMALL_WIN_TARGET  # Take profit at 5%
        self.quick_exit_threshold = config.ADMIN_QUICK_EXIT_THRESHOLD  # Max 10%
        
        # Track accumulated small wins
        self.small_wins_count = 0
        self.total_small_profits = 0.0
        
        # CRITICAL PROTECTION: Daily loss limits
        self.daily_loss_limit = config.ADMIN_DAILY_LOSS_LIMIT
        self.max_consecutive_losses = config.ADMIN_MAX_CONSECUTIVE_LOSSES
        self.daily_pnl = 0.0
        self.starting_balance = self.capital
        self.consecutive_losses = 0
        self.last_reset_date = datetime.utcnow().date()
        self.trading_paused = False
        
        logger.info(f"💰 Admin Auto-Trader initialized")
        logger.info(f"   Current Balance: ${self.capital:.2f} USDT")
        logger.info(f"   Min Trade: ${self.min_trade_size} | Max Trade: ${self.max_trade_size}")
        
        # Send startup notification
        if self.telegram and self.telegram.enabled:
            strategy_mode = "💎 SMALL PROFIT MODE" if self.small_profit_mode else "🎯 STANDARD MODE"
            strategy_details = f"Taking profits at {self.small_win_target}%-{self.quick_exit_threshold}%" if self.small_profit_mode else f"Target: {self.target_profit_per_trade}%"
            
            self.telegram.send_message(
                f"🤖 <b>ADMIN AUTO-TRADER STARTED</b>\n\n"
                f"💰 Current Balance: <b>${self.capital:.2f} USDT</b>\n"
                f"📊 Min Trade: ${self.min_trade_size} | Max: ${self.max_trade_size}\n\n"
                f"<b>{strategy_mode}</b>\n"
                f"✅ {strategy_details}\n"
                f"🛑 Stop Loss: {self.max_loss_per_trade}%\n\n"
                f"💡 <b>Many small wins = Big total profit!</b>\n"
                f"🎯 $0.50 × 10 trades = $5.00 profit\n\n"
                f"✅ Trading 24/7 - You'll be notified of all trades!"
            )
    
    def get_current_balance(self):
        """Get current USDT balance"""
        try:
            balance = self.exchange.fetch_balance()
            if not balance or 'USDT' not in balance:
                logger.error("Invalid balance data from exchange")
                return self.capital  # Return cached capital
            usdt_balance = balance.get('USDT', {}).get('free', 0)
            logger.info(f"💵 Current balance: ${usdt_balance:.2f} USDT")
            return usdt_balance
        except Exception as e:
            logger.error(f"❌ Error fetching balance: {e}")
            return 0
    
    def calculate_trade_size(self, balance):
        """Calculate optimal trade size"""
        # Use 90% of balance, but cap at max_trade_size
        trade_size = min(balance * 0.9, self.max_trade_size)
        
        # Ensure minimum trade size
        if trade_size < self.min_trade_size:
            logger.warning(f"⚠️ Balance too low for trading: ${balance:.2f}")
            # Send low balance notification (only once per hour to avoid spam)
            if self.telegram and self.telegram.enabled:
                if not hasattr(self, '_last_low_balance_alert') or \
                   (datetime.utcnow() - self._last_low_balance_alert).seconds > 3600:
                    self.telegram.send_message(
                        f"⚠️ <b>BALANCE TOO LOW</b>\n\n"
                        f"Current Balance: <b>${balance:.2f} USDT</b>\n"
                        f"Minimum Required: ${self.min_trade_size} USDT\n\n"
                        f"💡 Add funds to continue trading!\n"
                        f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                    )
                    self._last_low_balance_alert = datetime.utcnow()
            return 0
        
        return trade_size
    
    def run_new_listing_strategy(self):
        """
        Run new listing detection and trading
        This is the HIGH REWARD strategy for growing small capital
        """
        logger.info("🔍 Scanning for new listings...")
        
        # New listing bot already configured from config.py
        # No need to override unless balance-specific adjustment needed
        
        # Start monitoring
        try:
            self.new_listing_bot.start_monitoring()
            logger.info("✅ New listing bot started - will trade automatically!")
        except Exception as e:
            logger.error(f"❌ Error starting new listing bot: {e}")
    
    def run_momentum_strategy(self, balance):
        """
        Run momentum trading on BTC/ETH
        Use this when balance meets minimum threshold
        """
        if balance < self.momentum_min_balance:
            logger.info(f"💡 Balance ${balance:.2f} below ${self.momentum_min_balance} minimum for momentum trading")
            return
        
        logger.info("📈 Running momentum strategy on BTC/USDT...")
        
        try:
            # Fetch BTC price
            ticker = self.exchange.fetch_ticker('BTC/USDT')
            price = ticker['last']
            
            # 🔴 CRITICAL: Validate price before trading
            if price is None or price <= 0 or price == 0.0:
                logger.error(f"❌ Invalid BTC price: ${price} - SKIPPING TRADE!")
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_message(
                        f"⚠️ <b>INVALID PRICE DETECTED</b>\n\n"
                        f"Symbol: BTC/USDT\n"
                        f"Price: ${price}\n\n"
                        f"💡 Trade blocked for safety"
                    )
                return
            
            # AI ENHANCED: Use Advanced AI for comprehensive analysis
            should_enter = False
            ai_confidence = 70  # Default confidence
            adjusted_position_size = None
            
            if self.ai_engine:
                try:
                    # Multi-timeframe analysis
                    logger.info("🤖 Running AI multi-timeframe analysis...")
                    ai_analysis = self.ai_engine.should_enter_trade('BTC/USDT', 'buy', confidence=75)
                    
                    should_enter = ai_analysis['should_enter']
                    ai_confidence = ai_analysis['confidence_adjusted']
                    
                    logger.info(f"🤖 AI Decision: {'ENTER' if should_enter else 'SKIP'} (Confidence: {ai_confidence}%)")
                    logger.info(f"🤖 Reason: {ai_analysis['reason']}")
                    
                    if should_enter:
                        # Use smart position sizing based on confidence and volatility
                        volatility = ai_analysis['analysis'].get('volatility', 0.02)
                        adjusted_position_size = self.ai_engine.calculate_smart_position_size(
                            balance, ai_confidence, volatility
                        )
                        logger.info(f"💰 Smart Position Size: ${adjusted_position_size:.2f} (AI-optimized)")
                except Exception as e:
                    logger.warning(f"⚠️ AI analysis failed: {e} - using basic logic")
                    should_enter = self.is_momentum_bullish('BTC/USDT')
            else:
                # Fallback to basic momentum check
                should_enter = self.is_momentum_bullish('BTC/USDT')
            
            # Calculate position size (use AI recommendation if available)
            if adjusted_position_size:
                trade_size = min(adjusted_position_size, self.max_trade_size)
            else:
                trade_size = self.calculate_trade_size(balance)
            
            amount = trade_size / price
            
            # Check if we should enter
            if should_enter:
                confidence_str = f" (AI Confidence: {ai_confidence}%)" if self.ai_engine else ""
                logger.info(f"🚀 Bullish momentum detected{confidence_str}! Buying {amount:.6f} BTC")
                
                # Place order with SPOT params
                order = self.exchange.create_market_order(
                    'BTC/USDT', 
                    'buy', 
                    amount,
                    params={'tdMode': 'cash'}  # SPOT trading only
                )
                
                # AI ENHANCED: Calculate dynamic targets based on volatility
                if self.ai_engine and ai_analysis.get('analysis'):
                    try:
                        volatility = ai_analysis['analysis'].get('volatility', 0.02)
                        
                        # Dynamic stop loss
                        stop_loss_price, stop_pct = self.ai_engine.calculate_dynamic_stop_loss(
                            price, 'buy', volatility, ai_confidence
                        )
                        
                        # Dynamic take profit (3:1 risk-reward)
                        take_profit_price, tp_pct = self.ai_engine.calculate_dynamic_take_profit(
                            price, stop_loss_price, 'buy', risk_reward_ratio=3.0
                        )
                        
                        logger.info(f"🤖 AI Dynamic Targets: TP {tp_pct*100:.1f}%, SL {stop_pct*100:.1f}%")
                    except Exception as e:
                        logger.warning(f"⚠️ AI target calculation failed: {e} - using defaults")
                        take_profit_price = price * (1 + self.target_profit_per_trade / 100)
                        stop_loss_price = price * (1 - self.max_loss_per_trade / 100)
                else:
                    # Standard targets
                    take_profit_price = price * (1 + self.target_profit_per_trade / 100)
                    stop_loss_price = price * (1 - self.max_loss_per_trade / 100)
                
                # Calculate percentages for display
                tp_pct_display = ((take_profit_price - price) / price) * 100
                sl_pct_display = ((price - stop_loss_price) / price) * 100
                
                # Add to profit protector
                position_id = self.profit_protector.add_position(
                    symbol='BTC/USDT',
                    entry_price=price,
                    amount=amount,
                    side='long',
                    metadata={'strategy': 'momentum', 'admin': True}
                )
                
                logger.info(f"✅ Position opened and protected: {position_id}")
                
                # Send Telegram notification
                if self.telegram and self.telegram.enabled:
                    ai_info = ""
                    if self.ai_engine:
                        ai_info = (
                            f"\n🤖 <b>AI Analysis:</b>\n"
                            f"   Confidence: {ai_confidence}%\n"
                            f"   Multi-timeframe: Confirmed\n"
                            f"   Risk-Reward: 3:1 optimized\n"
                        )
                    
                    self.telegram.send_message(
                        f"🟢 <b>MOMENTUM TRADE - BUY</b>\n\n"
                        f"🪙 Symbol: <b>BTC/USDT</b>\n"
                        f"💰 Entry Price: <b>${price:,.2f}</b>\n"
                        f"📊 Amount: {amount:.6f} BTC\n"
                        f"💵 Trade Size: ${trade_size:.2f} USDT\n"
                        f"{ai_info}\n"
                        f"🎯 Take Profit: ${take_profit_price:,.2f} (+{tp_pct_display:.1f}%)\n"
                        f"🛑 Stop Loss: ${stop_loss_price:,.2f} (-{sl_pct_display:.1f}%)\n\n"
                        f"📈 Strategy: Momentum {'+ AI' if self.ai_engine else ''}\n"
                        f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                    )
                
                # Save trade
                self.db.db['admin_trades'].insert_one({
                    'symbol': 'BTC/USDT',
                    'side': 'buy',
                    'amount': amount,
                    'price': price,
                    'position_id': position_id,
                    'strategy': 'momentum',
                    'timestamp': datetime.utcnow()
                })
                
        except Exception as e:
            logger.error(f"❌ Error in momentum strategy: {e}")
            # Send error notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_message(
                    f"⚠️ <b>ERROR IN MOMENTUM STRATEGY</b>\n\n"
                    f"Failed to execute momentum trade.\n"
                    f"Error: {str(e)}\n\n"
                    f"Bot will continue monitoring.\n"
                    f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                )
    
    def is_momentum_bullish(self, symbol):
        """
        Check if momentum is bullish
        Simple check: price above 1-hour average
        """
        try:
            # Fetch recent candles
            candles = self.exchange.fetch_ohlcv(symbol, '5m', limit=12)  # Last hour
            
            # Calculate average
            closes = [c[4] for c in candles]
            avg_price = sum(closes) / len(closes)
            current_price = closes[-1]
            
            # Bullish if current > average
            return current_price > avg_price
            
        except Exception as e:
            logger.error(f"❌ Error checking momentum: {e}")
            return False
    
    def monitor_positions(self):
        """
        Monitor all open positions
        Profit protector handles exits automatically
        """
        try:
            # Get all active positions
            positions = self.profit_protector.active_positions
            
            if not positions:
                logger.info("📊 No active positions")
                return
            
            logger.info(f"📊 Monitoring {len(positions)} positions...")
            
            for pos_id, position in list(positions.items()):  # Bug #7 fix: list() prevents race condition
                # Fetch current price
                symbol = position.get('symbol')
                if not symbol:
                    logger.warning(f"Position missing symbol: {position}")
                    continue
                
                # Bug #6 fix: Null check on API response
                try:
                    ticker = self.exchange.fetch_ticker(symbol)
                    if not ticker or 'last' not in ticker:
                        logger.warning(f"Invalid ticker data for {symbol}")
                        continue
                    current_price = ticker['last']
                    
                    # 🔴 CRITICAL: Validate price is not zero or invalid
                    if current_price is None or current_price <= 0 or current_price == 0.0:
                        logger.error(f"❌ Invalid price for {symbol}: ${current_price} - SKIPPING!")
                        continue
                except Exception as e:
                    logger.error(f"Failed to fetch ticker for {symbol}: {e}")
                    continue
                
                # Check profit protector (returns single action dict)
                action = self.profit_protector.update_position(pos_id, current_price)
                
                # Calculate current P&L for monitoring
                entry_price = position.get('entry_price', 0)
                if entry_price <= 0:
                    logger.warning(f"Invalid entry_price for {symbol}: {entry_price}")
                    continue
                
                current_pnl_pct = ((current_price - entry_price) / entry_price) * 100
                amount = position.get('amount', 0)
                current_pnl_usd = (current_price - entry_price) * amount
                
                # SMALL PROFIT MODE: Auto-exit at small gains!
                if self.small_profit_mode:
                    # Take profit at small win target (5% default)
                    if current_pnl_pct >= self.small_win_target:
                        logger.info(f"💎 SMALL WIN! {symbol} up {current_pnl_pct:.1f}% - TAKING PROFIT!")
                        # Send notification about small win
                        if self.telegram and self.telegram.enabled:
                            try:
                                self.telegram.send_message(
                                    f"💎 <b>SMALL WIN - AUTO EXIT!</b>\n\n"
                                    f"🪙 Symbol: <b>{symbol}</b>\n"
                                    f"📈 Entry: ${entry_price:,.2f}\n"
                                    f"📊 Exit: ${current_price:,.2f}\n\n"
                                    f"<b>💰 Profit: +{current_pnl_usd:.2f} USD (+{current_pnl_pct:.1f}%)</b>\n\n"
                                    f"✅ Small profit taken automatically!\n"
                                    f"💡 Many small wins = Big total!\n\n"
                                    f"🎯 Total small wins today: {self.small_wins_count + 1}"
                                )
                            except:
                                pass
                        
                        # Execute exit
                        self.execute_exit(position, current_price, f"Small Win (+{current_pnl_pct:.1f}%)")
                        self.small_wins_count += 1
                        self.total_small_profits += current_pnl_usd
                        continue
                
                # AI SUGGESTION: Notify when significant profit (works in ALL modes now!)
                # Trigger thresholds: 5%, 10%, 15%, 20%, etc. (every 5%)
                if current_pnl_pct >= 5 and current_pnl_pct < self.target_profit_per_trade:
                    # Calculate milestone (5%, 10%, 15%, 20%, ...)
                    milestone = int(current_pnl_pct / 5) * 5
                    last_suggestion = position.get('_last_suggestion_pct', 0)
                    
                    # Send suggestion if we hit a new milestone
                    if milestone > last_suggestion and milestone >= 5:
                        if self.telegram and self.telegram.enabled:
                            try:
                                # AI ANALYSIS: Dynamic advice based on profit level
                                if current_pnl_pct >= 20:
                                    ai_advice = "🤖 AI: STRONG SELL SIGNAL - Lock in this excellent profit!"
                                    urgency = "🚨 HIGH"
                                elif current_pnl_pct >= 15:
                                    ai_advice = "🤖 AI: Consider selling - Good profit achieved"
                                    urgency = "⚠️ MEDIUM"
                                elif current_pnl_pct >= 10:
                                    ai_advice = "🤖 AI: Decent profit - Your decision to hold or sell"
                                    urgency = "💡 LOW"
                                else:  # 5%
                                    ai_advice = "🤖 AI: Early profit - May reach higher, but bird in hand..."
                                    urgency = "ℹ️ INFO"
                                
                                self.telegram.send_message(
                                    f"💡 <b>AI PROFIT SUGGESTION</b>\n\n"
                                    f"🪙 Symbol: <b>{symbol}</b>\n"
                                    f"📈 Entry: ${entry_price:,.2f}\n"
                                    f"📊 Current: ${current_price:,.2f}\n"
                                    f"📈 Change: <b>+{(current_price - entry_price):,.2f} (+{current_pnl_pct:.1f}%)</b>\n\n"
                                    f"<b>💰 Profit: +${current_pnl_usd:.2f} USD</b>\n\n"
                                    f"🎯 Target: +{self.target_profit_per_trade}%\n"
                                    f"🛡️ Stop Loss: -{self.max_loss_per_trade}%\n"
                                    f"⏱️ Time Held: {self._get_time_held(position)}\n\n"
                                    f"{ai_advice}\n"
                                    f"🔔 Urgency: {urgency}\n\n"
                                    f"✅ <b>Option 1:</b> Sell now (secure ${current_pnl_usd:.2f})\n"
                                    f"⏳ <b>Option 2:</b> Hold for {self.target_profit_per_trade}% target\n\n"
                                    f"🤖 <i>AI analyzes market conditions to help you decide!</i>"
                                )
                                position['_last_suggestion_pct'] = milestone
                                logger.info(f"📱 AI suggestion sent at {current_pnl_pct:.1f}% (milestone: {milestone}%)")
                            except Exception as e:
                                logger.error(f"Failed to send AI suggestion: {e}")
                
                # Execute profit protector actions
                if action and action.get('action'):
                    action_type = action['action']
                    
                    if action_type == 'close_all':
                        logger.info(f"🛡️ Profit protector triggered exit: {action['reason']}")
                        # Send notification about profit protector action
                        if self.telegram and self.telegram.enabled:
                            try:
                                self.telegram.send_message(
                                    f"🛡️ <b>PROFIT PROTECTOR - AUTO EXIT</b>\n\n"
                                    f"🪙 Symbol: <b>{symbol}</b>\n"
                                    f"📊 Reason: <b>{action['reason']}</b>\n"
                                    f"💰 Exit Price: ${current_price:,.2f}\n"
                                    f"📈 P&L: {current_pnl_pct:+.1f}%\n\n"
                                    f"✅ Protection system working!\n"
                                    f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                                )
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to send protector notification: {e}")
                        
                        self.execute_exit(position, current_price, action['reason'])
                        continue
                        
                    elif action_type == 'partial_close':
                        logger.info(f"💰 Profit protector taking partial profit: {action['reason']}")
                        # Send notification about partial profit
                        if self.telegram and self.telegram.enabled:
                            try:
                                partial_pct = (action['amount'] / position.get('amount', 1)) * 100
                                self.telegram.send_message(
                                    f"💰 <b>PARTIAL PROFIT TAKEN</b>\n\n"
                                    f"🪙 Symbol: <b>{symbol}</b>\n"
                                    f"📊 Selling: <b>{partial_pct:.0f}%</b> of position\n"
                                    f"📈 Reason: {action['reason']}\n"
                                    f"💵 Price: ${current_price:,.2f}\n\n"
                                    f"✅ Securing gains!\n"
                                    f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                                )
                            except Exception as e:
                                logger.warning(f"⚠️ Failed to send partial profit notification: {e}")
                        
                        self.execute_partial_exit(position, action['amount'], current_price)
                
        except Exception as e:
            logger.error(f"❌ Error monitoring positions: {e}")
    
    def execute_exit(self, position, price, reason):
        """Execute full exit"""
        try:
            symbol = position.get('symbol')
            amount = position.get('amount', 0)
            
            if not symbol or amount <= 0:
                logger.error(f"❌ Invalid position data for exit: {position}")
                return
            
            # 🔴 CRITICAL: Execute sell order with SPOT params and error handling
            try:
                order = self.exchange.create_market_order(
                    symbol, 
                    'sell', 
                    amount,
                    params={'tdMode': 'cash'}  # SPOT trading only
                )
                logger.info(f"✅ SELL order executed on exchange: {symbol} - {amount} @ ${price:.4f}")
            except Exception as e:
                logger.error(f"❌ CRITICAL: Failed to execute sell order for {symbol}: {e}")
                
                # Send urgent alert
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_message(
                        f"🚨 <b>SELL ORDER FAILED!</b>\n\n"
                        f"Symbol: {symbol}\n"
                        f"Amount: {amount}\n"
                        f"Price: ${price:.4f}\n"
                        f"Reason: {reason}\n\n"
                        f"Error: {str(e)}\n\n"
                        f"⚠️ CHECK OKX MANUALLY!"
                    )
                return  # Don't update P&L if sell failed
            
            # Calculate P&L
            entry_price = position.get('entry_price', 0)
            if entry_price <= 0:
                logger.error(f"Invalid entry_price: {entry_price}")
                return
            
            pnl_pct = ((price - entry_price) / entry_price) * 100
            pnl_usd = (price - entry_price) * amount
            
            # Determine emoji and message tone
            is_profit = pnl_usd > 0
            emoji = "✅" if is_profit else "❌"
            status_emoji = "🟢" if is_profit else "🔴"
            
            # Track consecutive losses for daily limit protection
            if is_profit:
                self.consecutive_losses = 0  # Reset on win
            else:
                self.consecutive_losses += 1  # Increment on loss
            
            # Update daily P&L
            self.daily_pnl += pnl_usd
            
            logger.info(f"{emoji} Position closed: {symbol} | P&L: {pnl_pct:.2f}% (${pnl_usd:.2f})")
            
            # Send comprehensive Telegram notifications
            if self.telegram and self.telegram.enabled:
                if is_profit:
                    # Check if this is a small win (5% auto-exit)
                    if self.small_profit_mode and 4.5 <= pnl_pct <= 6:
                        self.telegram.send_small_win(
                            symbol=symbol,
                            entry=entry_price,
                            exit=price,
                            profit_usd=pnl_usd,
                            profit_pct=pnl_pct,
                            total_small_wins=self.small_wins_count,
                            accumulated_profit=self.total_small_profits
                        )
                    # Check if this is a trailing stop
                    elif "trailing" in reason.lower():
                        peak_price = position.get('highest_price', price)
                        self.telegram.send_trailing_stop_hit(
                            symbol=symbol,
                            entry=entry_price,
                            peak=peak_price,
                            exit=price,
                            profit_usd=pnl_usd,
                            profit_pct=pnl_pct
                        )
                    else:
                        # Regular profit exit
                        self.telegram.send_position_closed({
                            'symbol': symbol,
                            'entry_price': entry_price,
                            'exit_price': price,
                            'pnl': pnl_usd,
                            'pnl_percent': pnl_pct,
                            'exit_reason': reason
                        })
                else:
                    # Loss - use stop loss notification
                    self.telegram.send_stop_loss_hit(
                        symbol=symbol,
                        entry=entry_price,
                        exit=price,
                        loss_usd=abs(pnl_usd),
                        loss_pct=abs(pnl_pct)
                    )
            
            # Save trade result
            self.db.db['admin_trades'].insert_one({
                'symbol': symbol,
                'side': 'sell',
                'amount': amount,
                'entry_price': entry_price,
                'exit_price': price,
                'pnl_percent': pnl_pct,
                'pnl_usd': pnl_usd,
                'exit_reason': reason,
                'timestamp': datetime.utcnow()
            })
            
            # Remove from profit protector
            self.profit_protector.remove_position(position['id'])
            
        except Exception as e:
            logger.error(f"❌ Error executing exit: {e}")
            # Send error notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_order_failed(
                    symbol=position.get('symbol', 'Unknown'),
                    side='SELL',
                    amount=position.get('amount', 0),
                    reason=str(e)
                )
    
    def execute_partial_exit(self, position, amount, price):
        """Execute partial exit"""
        try:
            symbol = position.get('symbol')
            if not symbol or amount <= 0:
                logger.error(f"❌ Invalid partial exit params: symbol={symbol}, amount={amount}")
                return
            
            # 🔴 CRITICAL: Execute partial sell order with SPOT params and error handling
            try:
                order = self.exchange.create_market_order(
                    symbol, 
                    'sell', 
                    amount,
                    params={'tdMode': 'cash'}  # SPOT trading only
                )
                logger.info(f"✅ PARTIAL SELL executed on exchange: {symbol} - {amount} @ ${price:.4f}")
            except Exception as e:
                logger.error(f"❌ CRITICAL: Failed to execute partial sell for {symbol}: {e}")
                
                # Send urgent alert
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_message(
                        f"🚨 <b>PARTIAL SELL FAILED!</b>\n\n"
                        f"Symbol: {symbol}\n"
                        f"Amount: {amount}\n"
                        f"Price: ${price:.4f}\n\n"
                        f"Error: {str(e)}\n\n"
                        f"⚠️ CHECK OKX MANUALLY!"
                    )
                return  # Don't update position if sell failed
            
            # Calculate P&L
            entry_price = position.get('entry_price', 0)
            if entry_price <= 0:
                logger.error(f"Invalid entry_price: {entry_price}")
                return
            
            pnl_pct = ((price - entry_price) / entry_price) * 100
            pnl_usd = (price - entry_price) * amount
            
            logger.info(f"💰 Partial profit taken: {symbol} | {pnl_pct:.2f}% (${pnl_usd:.2f})")
            
            # Update position first
            original_amount = position.get('amount', 0)
            remaining_amount = original_amount - amount
            percent_sold = (amount / original_amount * 100) if original_amount > 0 else 0
            
            # Send comprehensive Telegram notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_partial_profit(
                    symbol=symbol,
                    percent_sold=int(percent_sold),
                    profit_usd=pnl_usd,
                    profit_pct=pnl_pct,
                    remaining_amount=remaining_amount
                )
            
            # Update position
            position['amount'] = remaining_amount
            
        except Exception as e:
            logger.error(f"❌ Error executing partial exit: {e}")
    
    def _get_time_held(self, position):
        """Calculate how long position has been held"""
        try:
            entry_time = position.get('entry_time', datetime.utcnow())
            if isinstance(entry_time, str):
                entry_time = datetime.fromisoformat(entry_time)
            
            time_held = datetime.utcnow() - entry_time
            hours = time_held.total_seconds() / 3600
            
            if hours < 1:
                minutes = time_held.total_seconds() / 60
                return f"{minutes:.0f} min"
            elif hours < 24:
                return f"{hours:.1f} hours"
            else:
                days = hours / 24
                return f"{days:.1f} days"
        except:
            return "Unknown"
            # Send error notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_message(
                    f"🚨 <b>ERROR - PARTIAL EXIT FAILED</b>\n\n"
                    f"Symbol: {position.get('symbol', 'Unknown')}\n"
                    f"Error: {str(e)}\n\n"
                    f"⚠️ Manual intervention may be required!"
                )
    
    def check_daily_limits(self):
        """CRITICAL: Check daily loss limits to protect users!"""
        # Reset daily tracking if new day
        current_date = datetime.utcnow().date()
        if current_date > self.last_reset_date:
            self.daily_pnl = 0.0
            self.consecutive_losses = 0
            self.last_reset_date = current_date
            self.trading_paused = False
            self.starting_balance = self.get_current_balance()
            logger.info("📅 New day - Daily limits reset")
        
        # Check daily loss limit
        current_balance = self.get_current_balance()
        daily_loss_pct = ((current_balance - self.starting_balance) / self.starting_balance) * 100 if self.starting_balance > 0 else 0
        
        if daily_loss_pct <= -self.daily_loss_limit:
            if not self.trading_paused:
                self.trading_paused = True
                logger.error(f"🚨 DAILY LOSS LIMIT! Lost {daily_loss_pct:.2f}%")
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_daily_limit_reached(
                        loss_pct=abs(daily_loss_pct),
                        starting_balance=self.starting_balance,
                        current_balance=current_balance,
                        loss_amount=abs(self.starting_balance - current_balance)
                    )
            return False
        
        # Check consecutive loss limit
        if self.consecutive_losses >= self.max_consecutive_losses:
            logger.warning(f"⚠️ {self.consecutive_losses} consecutive losses - Taking 1 hour break")
            if self.telegram and self.telegram.enabled:
                self.telegram.send_consecutive_losses_warning(
                    losses_count=self.consecutive_losses,
                    pause_duration_mins=60
                )
            time.sleep(3600)
            self.consecutive_losses = 0
            return True
        
        return True
    
    def run_forever(self):
        """
        Main loop - runs 24/7
        Automatically grows your capital while you sleep
        """
        logger.info("🚀 Starting Admin Auto-Trader...")
        logger.info("💤 You can sleep now - I'll make you money!")
        
        # Start new listing bot (runs in background)
        self.run_new_listing_strategy()
        
        while True:
            try:
                # CRITICAL: Check daily loss limits FIRST!
                if not self.check_daily_limits():
                    logger.info("⏸️ Trading paused - Daily loss limit reached")
                    time.sleep(3600)  # Check again in 1 hour
                    continue
                
                # Get current balance
                balance = self.get_current_balance()
                
                # Update capital
                self.capital = balance
                
                # Log progress
                logger.info(f"💰 Current capital: ${balance:.2f} USDT")
                
                # Monitor existing positions
                self.monitor_positions()
                
                # Run momentum strategy if balance meets minimum
                if balance >= self.momentum_min_balance:
                    self.run_momentum_strategy(balance)
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Stopping Admin Auto-Trader...")
                # Send stop notification
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_message(
                        f"🛑 <b>ADMIN AUTO-TRADER STOPPED</b>\n\n"
                        f"Trading bot has been stopped manually.\n\n"
                        f"⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    )
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                # Send critical error notification
                if self.telegram and self.telegram.enabled:
                    self.telegram.send_message(
                        f"🚨 <b>CRITICAL ERROR IN AUTO-TRADER</b>\n\n"
                        f"Error: {str(e)}\n\n"
                        f"Bot will retry in 60 seconds.\n"
                        f"⚠️ Check logs if this persists!\n\n"
                        f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                    )
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    trader = AdminAutoTrader()
    trader.run_forever()
