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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # Get exchange
        if is_admin:
            exchange = self.system_exchange
        else:
            user = self.db.db['users'].find_one({"_id": ObjectId(user_id)})
            if not user or not user.get('exchange_connected'):
                raise ValueError("Connect OKX first")
            creds = user.get('okx_credentials', {})
            exchange = ccxt.okx({
                'apiKey': creds.get('api_key'),
                'secret': creds.get('secret'),
                'password': creds.get('passphrase'),
                'enableRateLimit': True
            })
        
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
        self.balance = config.get('capital', 1000)
        self.symbol = config.get('symbol', 'BTC/USDT')
    
    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self.trading_loop())
    
    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
    
    async def trading_loop(self):
        """Main trading loop with real execution"""
        position = None
        
        while self.running:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                price = ticker['last']
                
                # Simple momentum strategy
                if not position:
                    # Open position
                    amount = (self.balance * 0.9) / price
                    
                    # Check minimum order value (OKX requires minimum $5)
                    order_value = amount * price
                    if order_value < 5 and not self.paper_trading:
                        logger.warning(f"⚠️ Order value ${order_value:.2f} too small, minimum $5. Skipping.")
                        await asyncio.sleep(60)
                        continue
                    
                    if self.paper_trading:
                        logger.info(f"📝 PAPER BUY: {amount:.6f} {self.symbol} @ ${price:.2f}")
                    else:
                        order = self.exchange.create_market_order(self.symbol, 'buy', amount)
                        logger.info(f"💰 REAL BUY: {amount:.6f} {self.symbol} @ ${price:.2f}")
                    
                    position = {'entry': price, 'amount': amount, 'time': datetime.utcnow()}
                    
                    # Save trade
                    trade_doc = {
                        'bot_id': self.bot_id,
                        'user_id': self.user_id,
                        'symbol': self.symbol,
                        'side': 'buy',
                        'amount': amount,
                        'price': price,
                        'is_paper': self.paper_trading,
                        'timestamp': datetime.utcnow()
                    }
                    self.db.db['trades'].insert_one(trade_doc)
                    
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
                    # Check exit conditions
                    pnl_pct = ((price - position['entry']) / position['entry']) * 100
                    
                    if pnl_pct >= 2.0 or pnl_pct <= -1.0:  # 2% profit or 1% loss
                        if self.paper_trading:
                            logger.info(f"📝 PAPER SELL: {position['amount']:.6f} @ ${price:.2f} | PnL: {pnl_pct:.2f}%")
                        else:
                            order = self.exchange.create_market_order(self.symbol, 'sell', position['amount'])
                            logger.info(f"💰 REAL SELL: {position['amount']:.6f} @ ${price:.2f} | PnL: {pnl_pct:.2f}%")
                        
                        # Save trade
                        self.db.db['trades'].insert_one({
                            'bot_id': self.bot_id,
                            'user_id': self.user_id,
                            'symbol': self.symbol,
                            'side': 'sell',
                            'amount': position['amount'],
                            'price': price,
                            'pnl_percent': pnl_pct,
                            'is_paper': self.paper_trading,
                            'timestamp': datetime.utcnow()
                        })
                        
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
                logger.error(f"Error: {e}")
                await asyncio.sleep(60)

# Global instance
bot_engine = TradingBotEngine()
