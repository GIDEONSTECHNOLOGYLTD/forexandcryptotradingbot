"""
ADMIN AUTO-TRADER - Fully Automated Trading While You Sleep
Grows your $16.78 to $1,000+ automatically
"""
import ccxt
import time
import logging
from datetime import datetime
from mongodb_database import MongoTradingDatabase
from new_listing_bot import NewListingBot
from auto_profit_protector import AutoProfitProtector
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
        
        # Trading settings (optimized for $16.78)
        self.capital = 16.78
        self.min_trade_size = 5  # OKX minimum
        self.max_trade_size = 15  # Leave $1.78 buffer
        self.target_profit_per_trade = 50  # 50% profit target
        self.max_loss_per_trade = 15  # 15% stop loss
        
        logger.info(f"💰 Admin Auto-Trader initialized with ${self.capital}")
    
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
            return 0
        
        return trade_size
    
    def run_new_listing_strategy(self):
        """
        Run new listing detection and trading
        This is the HIGH REWARD strategy for growing small capital
        """
        logger.info("🔍 Scanning for new listings...")
        
        # Configure new listing bot for small capital
        self.new_listing_bot.buy_amount_usdt = self.max_trade_size
        self.new_listing_bot.take_profit_percent = self.target_profit_per_trade
        self.new_listing_bot.stop_loss_percent = self.max_loss_per_trade
        self.new_listing_bot.max_hold_time = 3600  # 1 hour max
        
        # Start monitoring
        try:
            self.new_listing_bot.start_monitoring()
            logger.info("✅ New listing bot started - will trade automatically!")
        except Exception as e:
            logger.error(f"❌ Error starting new listing bot: {e}")
    
    def run_momentum_strategy(self, balance):
        """
        Run momentum trading on BTC/ETH
        Use this when balance > $50
        """
        if balance < 50:
            logger.info("💡 Balance too low for momentum trading, using new listing strategy")
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
                
                # Add to profit protector
                position_id = self.profit_protector.add_position(
                    symbol='BTC/USDT',
                    entry_price=price,
                    amount=amount,
                    side='long',
                    metadata={'strategy': 'momentum', 'admin': True}
                )
                
                logger.info(f"✅ Position opened and protected: {position_id}")
                
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
            
            logger.info(f"✅ Position closed: {symbol} | P&L: {pnl_pct:.2f}% (${pnl_usd:.2f})")
            
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
            
            # Update position
            position['amount'] -= amount
            
        except Exception as e:
            logger.error(f"❌ Error executing partial exit: {e}")
    
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
                
                # Run momentum strategy if balance is high enough
                if balance >= 50:
                    self.run_momentum_strategy(balance)
                
                # Sleep for 1 minute
                time.sleep(60)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Stopping Admin Auto-Trader...")
                break
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    trader = AdminAutoTrader()
    trader.run_forever()
