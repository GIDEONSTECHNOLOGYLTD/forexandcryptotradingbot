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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        self.profit_protector = AutoProfitProtector(self.exchange, self.db)
        
        # Initialize Telegram notifications
        self.telegram = TelegramNotifier()
        
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
            usdt_balance = balance['USDT']['free']
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
            
            # Calculate position size
            trade_size = self.calculate_trade_size(balance)
            amount = trade_size / price
            
            # Check if we should enter
            # Simple momentum: buy if price is trending up
            if self.is_momentum_bullish('BTC/USDT'):
                logger.info(f"🚀 Bullish momentum detected! Buying {amount:.6f} BTC")
                
                # Place order
                order = self.exchange.create_market_order('BTC/USDT', 'buy', amount)
                
                # Calculate targets
                take_profit_price = price * (1 + self.target_profit_per_trade / 100)
                stop_loss_price = price * (1 - self.max_loss_per_trade / 100)
                
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
                    self.telegram.send_message(
                        f"🟢 <b>MOMENTUM TRADE - BUY</b>\n\n"
                        f"🪙 Symbol: <b>BTC/USDT</b>\n"
                        f"💰 Entry Price: <b>${price:,.2f}</b>\n"
                        f"📊 Amount: {amount:.6f} BTC\n"
                        f"💵 Trade Size: ${trade_size:.2f} USDT\n\n"
                        f"🎯 Take Profit: ${take_profit_price:,.2f} (+{self.target_profit_per_trade}%)\n"
                        f"🛑 Stop Loss: ${stop_loss_price:,.2f} (-{self.max_loss_per_trade}%)\n\n"
                        f"📈 Strategy: Momentum\n"
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
            
            for pos_id, position in positions.items():
                # Fetch current price
                symbol = position['symbol']
                ticker = self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # Check profit protector
                actions = self.profit_protector.check_position(pos_id, current_price)
                
                # Calculate current P&L for monitoring
                entry_price = position['entry_price']
                current_pnl_pct = ((current_price - entry_price) / entry_price) * 100
                current_pnl_usd = (current_price - entry_price) * position['amount']
                
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
                
                # AI SUGGESTION: Notify when significant profit (let user decide) - Only in standard mode
                if not self.small_profit_mode and current_pnl_pct >= 10 and current_pnl_pct < self.target_profit_per_trade:
                    # Send suggestion notification (once per 5% gain to avoid spam)
                    if not hasattr(position, '_last_suggestion_pct') or \
                       current_pnl_pct - position.get('_last_suggestion_pct', 0) >= 5:
                        if self.telegram and self.telegram.enabled:
                            try:
                                self.telegram.send_message(
                                    f"💡 <b>AI SUGGESTION - CONSIDER SELLING</b>\n\n"
                                    f"🪙 Symbol: <b>{symbol}</b>\n"
                                    f"📈 Entry: ${entry_price:,.2f}\n"
                                    f"📊 Current: ${current_price:,.2f}\n\n"
                                    f"<b>💰 Current Profit: +{current_pnl_usd:.2f} USD (+{current_pnl_pct:.1f}%)</b>\n\n"
                                    f"🎯 Target: +{self.target_profit_per_trade}%\n\n"
                                    f"💡 <b>You're up {current_pnl_pct:.1f}%!</b>\n"
                                    f"✅ Consider taking profit now\n"
                                    f"⚠️ Or hold for {self.target_profit_per_trade}% target\n\n"
                                    f"🤖 You decide - I'm just suggesting!"
                                )
                                position['_last_suggestion_pct'] = current_pnl_pct
                                logger.info(f"📱 Sent AI profit suggestion at {current_pnl_pct:.1f}%")
                            except:
                                pass
                
                # Execute any actions
                if actions:
                    for action in actions:
                        if action['action'] == 'exit':
                            logger.info(f"🛡️ Profit protector triggered exit: {action['reason']}")
                            self.execute_exit(position, current_price, action['reason'])
                        elif action['action'] == 'partial_exit':
                            logger.info(f"💰 Taking partial profit: {action['amount']}")
                            self.execute_partial_exit(position, action['amount'], current_price)
                
        except Exception as e:
            logger.error(f"❌ Error monitoring positions: {e}")
    
    def execute_exit(self, position, price, reason):
        """Execute full exit"""
        try:
            symbol = position['symbol']
            amount = position['amount']
            
            # Place sell order
            order = self.exchange.create_market_order(symbol, 'sell', amount)
            
            # Calculate P&L
            entry_price = position['entry_price']
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
            
            # Send Telegram notification with accumulated profits
            if self.telegram and self.telegram.enabled:
                accumulated_msg = ""
                if self.small_profit_mode and is_profit:
                    accumulated_msg = f"\n💎 <b>Total accumulated: ${self.total_small_profits:.2f} from {self.small_wins_count} wins!</b>\n"
                
                self.telegram.send_message(
                    f"{status_emoji} <b>POSITION CLOSED</b> {emoji}\n\n"
                    f"🪙 Symbol: <b>{symbol}</b>\n"
                    f"📈 Entry: ${entry_price:,.2f}\n"
                    f"📉 Exit: ${price:,.2f}\n"
                    f"📊 Amount: {amount:.6f}\n\n"
                    f"<b>{'💰 PROFIT' if is_profit else '💸 LOSS'}: {pnl_usd:+.2f} USD ({pnl_pct:+.2f}%)</b>\n\n"
                    f"📌 Reason: {reason.upper()}\n"
                    f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}\n\n"
                    f"{'🎉 Great trade!' if is_profit else '⚠️ Review and adjust strategy'}"
                    f"{accumulated_msg}"
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
                self.telegram.send_message(
                    f"🚨 <b>ERROR CLOSING POSITION</b>\n\n"
                    f"Symbol: {position.get('symbol', 'Unknown')}\n"
                    f"Error: {str(e)}\n\n"
                    f"⚠️ Check your exchange account immediately!"
                )
    
    def execute_partial_exit(self, position, amount, price):
        """Execute partial exit"""
        try:
            symbol = position['symbol']
            
            # Place sell order
            order = self.exchange.create_market_order(symbol, 'sell', amount)
            
            # Calculate P&L
            entry_price = position['entry_price']
            pnl_pct = ((price - entry_price) / entry_price) * 100
            pnl_usd = (price - entry_price) * amount
            
            logger.info(f"💰 Partial profit taken: {symbol} | {pnl_pct:.2f}% (${pnl_usd:.2f})")
            
            # Send Telegram notification
            if self.telegram and self.telegram.enabled:
                self.telegram.send_message(
                    f"💰 <b>PARTIAL PROFIT TAKEN</b>\n\n"
                    f"🪙 Symbol: <b>{symbol}</b>\n"
                    f"📈 Entry: ${entry_price:,.2f}\n"
                    f"📉 Exit: ${price:,.2f}\n"
                    f"📊 Amount Sold: {amount:.6f}\n\n"
                    f"<b>💵 Profit: +{pnl_usd:.2f} USD (+{pnl_pct:.2f}%)</b>\n\n"
                    f"✅ Locking in profits! Position still open.\n"
                    f"⏰ {datetime.utcnow().strftime('%H:%M:%S UTC')}"
                )
            
            # Update position
            position['amount'] -= amount
            
        except Exception as e:
            logger.error(f"❌ Error executing partial exit: {e}")
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
                    self.telegram.send_message(
                        f"🚨 <b>DAILY LOSS LIMIT REACHED!</b>\n\n"
                        f"Lost: {abs(daily_loss_pct):.2f}% today\n"
                        f"Limit: {self.daily_loss_limit}%\n\n"
                        f"Starting: ${self.starting_balance:.2f}\n"
                        f"Current: ${current_balance:.2f}\n"
                        f"Loss: ${abs(self.starting_balance - current_balance):.2f}\n\n"
                        f"🛑 <b>TRADING PAUSED UNTIL TOMORROW!</b>\n\n"
                        f"⏰ Resumes: Tomorrow 00:00 UTC"
                    )
            return False
        
        # Check consecutive loss limit
        if self.consecutive_losses >= self.max_consecutive_losses:
            logger.warning(f"⚠️ {self.consecutive_losses} consecutive losses - Taking 1 hour break")
            if self.telegram and self.telegram.enabled:
                self.telegram.send_message(
                    f"⚠️ <b>CONSECUTIVE LOSS LIMIT</b>\n\n"
                    f"Losses in a row: {self.consecutive_losses}\n\n"
                    f"🛑 Pausing for 1 hour\n"
                    f"⏰ Resumes at: {(datetime.utcnow() + timedelta(hours=1)).strftime('%H:%M UTC')}"
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
