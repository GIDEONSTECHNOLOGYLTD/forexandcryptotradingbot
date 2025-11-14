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
        
        logger.info(f"💰 Admin Auto-Trader initialized")
        logger.info(f"   Current Balance: ${self.capital:.2f} USDT")
        logger.info(f"   Min Trade: ${self.min_trade_size} | Max Trade: ${self.max_trade_size}")
        
        # Send startup notification
        if self.telegram and self.telegram.enabled:
            self.telegram.send_message(
                f"🤖 <b>ADMIN AUTO-TRADER STARTED</b>\n\n"
                f"💰 Current Balance: <b>${self.capital:.2f} USDT</b>\n"
                f"📊 Min Trade: ${self.min_trade_size} | Max: ${self.max_trade_size}\n"
                f"🎯 Target Profit: {self.target_profit_per_trade}%\n"
                f"🛑 Stop Loss: {self.max_loss_per_trade}%\n\n"
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
            
            logger.info(f"{emoji} Position closed: {symbol} | P&L: {pnl_pct:.2f}% (${pnl_usd:.2f})")
            
            # Send Telegram notification
            if self.telegram and self.telegram.enabled:
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
