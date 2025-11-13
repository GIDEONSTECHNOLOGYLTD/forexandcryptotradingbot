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
    
    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
        
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
                ticker = self.exchange.fetch_ticker(self.symbol)
                price = ticker['last']
                
                # Simple momentum strategy
                if not position:
                    # Open position - USE ONLY YOUR ACTUAL BALANCE, NO LEVERAGE!
                    # Get fresh balance to ensure accuracy
                    if not self.paper_trading:
                        try:
                            balance_info = self.exchange.fetch_balance()
                            actual_usdt = balance_info['free']['USDT']
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
                        await asyncio.sleep(60)
                        continue
                    
                    if self.paper_trading:
                        logger.info(f"📝 PAPER BUY: {amount:.6f} {self.symbol} @ ${price:.2f}")
                    else:
                        # CRITICAL: Use spot market order (no margin/leverage)
                        order = self.exchange.create_market_order(
                            self.symbol, 
                            'buy', 
                            amount,
                            params={'tdMode': 'cash'}  # SPOT trading only!
                        )
                        logger.info(f"💰 SPOT BUY (NO LEVERAGE): {amount:.6f} {self.symbol} @ ${price:.2f}")
                        logger.info(f"📊 Used ${order_value:.2f} of your ${actual_usdt:.2f} balance")
                    
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
                
                elif position:
                    # Check profit protector first (automated protection)
                    should_exit = False
                    exit_reason = "manual"
                    
                    if self.profit_protector and position.get('protector_id'):
                        try:
                            # Update current price and check for exit signals
                            action = self.profit_protector.update_position(position['protector_id'], price)
                            if action and action.get('action') == 'exit':
                                should_exit = True
                                exit_reason = action.get('reason', 'profit_protector')
                                logger.info(f"🛡️ Profit protector triggered exit: {exit_reason}")
                        except Exception as e:
                            logger.warning(f"⚠️ Profit protector check failed: {e}")
                    
                    # Fallback to basic exit conditions if protector not active
                    if not should_exit:
                        pnl_pct = ((price - position['entry']) / position['entry']) * 100
                        if pnl_pct >= 2.0 or pnl_pct <= -1.0:  # 2% profit or 1% loss
                            should_exit = True
                            exit_reason = f"pnl_{pnl_pct:.2f}%"
                    
                    if should_exit:
                        # Calculate final P&L
                        final_pnl_pct = ((price - position['entry']) / position['entry']) * 100
                        
                        if self.paper_trading:
                            logger.info(f"📝 PAPER SELL: {position['amount']:.6f} @ ${price:.2f} | PnL: {final_pnl_pct:.2f}% | Reason: {exit_reason}")
                        else:
                            # CRITICAL: Use spot market order (no margin/leverage)
                            order = self.exchange.create_market_order(
                                self.symbol, 
                                'sell', 
                                position['amount'],
                                params={'tdMode': 'cash'}  # SPOT trading only!
                            )
                            logger.info(f"💰 SPOT SELL (NO LEVERAGE): {position['amount']:.6f} @ ${price:.2f} | PnL: {final_pnl_pct:.2f}% | Reason: {exit_reason}")
                        
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
                                    'pnl': pnl_pct,
                                    'mode': 'paper' if self.paper_trading else 'real'
                                }
                            })
                        except:
                            pass
                        
                        position = None
                
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
