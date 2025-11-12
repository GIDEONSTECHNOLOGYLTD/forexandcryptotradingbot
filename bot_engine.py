"""
Trading Bot Engine - Real & Paper Trading
"""
import ccxt
import asyncio
from datetime import datetime
from typing import Dict, Optional
import config
from mongodb_database import MongoTradingDatabase
from bson import ObjectId

class TradingBotEngine:
    def __init__(self):
        self.db = MongoTradingDatabase()
        self.active_bots: Dict[str, 'BotInstance'] = {}
        self.system_exchange = self._init_system_exchange()
        
    def _init_system_exchange(self):
        """Initialize system OKX for admin"""
        try:
            return ccxt.okx({
                'apiKey': config.OKX_API_KEY,
                'secret': config.OKX_SECRET_KEY,
                'password': config.OKX_PASSPHRASE,
                'enableRateLimit': True
            })
        except Exception as e:
            print(f"❌ System OKX init failed: {e}")
            return None
    
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
        """Main trading loop"""
        while self.running:
            try:
                ticker = self.exchange.fetch_ticker(self.symbol)
                price = ticker['last']
                
                # Simple strategy placeholder
                print(f"Bot {self.bot_id}: Price {price} ({'paper' if self.paper_trading else 'real'})")
                
                await asyncio.sleep(60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(60)

# Global instance
bot_engine = TradingBotEngine()
