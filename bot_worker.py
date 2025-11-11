"""
Trading Bot Background Worker
Runs all active bots and executes real trades
"""
import asyncio
import logging
from datetime import datetime
from colorama import Fore, Style
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import database
from mongodb_database import MongoTradingDatabase

# Import bot manager
from user_bot_manager import BotManager

# Import trading modules
try:
    from forex_trader import ForexTrader
    from grid_trading_bot import GridTradingBot, DCABot, ArbitrageBot
    ADVANCED_MODULES = True
except ImportError:
    ADVANCED_MODULES = False
    logger.warning("Advanced trading modules not available")


class TradingBotWorker:
    """
    Background worker that runs all active trading bots
    """
    
    def __init__(self):
        self.db = MongoTradingDatabase()
        self.bot_manager = BotManager(self.db.db)
        self.running = True
        
        print(f"{Fore.GREEN}╔════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.GREEN}║           TRADING BOT WORKER - PRODUCTION MODE                     ║{Style.RESET_ALL}")
        print(f"{Fore.GREEN}╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
        print()
    
    async def start(self):
        """Start the worker"""
        logger.info("🚀 Starting Trading Bot Worker...")
        
        # Load all active bots from database
        await self.load_active_bots()
        
        # Start main loop
        await self.main_loop()
    
    async def load_active_bots(self):
        """Load all active bots from database and start them"""
        try:
            # Find all bots with status "running"
            active_bots = list(self.db.db['bot_instances'].find({'status': 'running'}))
            
            logger.info(f"Found {len(active_bots)} active bots")
            
            for bot_doc in active_bots:
                try:
                    user_id = bot_doc['user_id']
                    bot_id = str(bot_doc['_id'])
                    
                    logger.info(f"Starting bot {bot_id} for user {user_id}")
                    
                    # Start bot using bot manager
                    await self.bot_manager.start_bot(user_id, bot_id)
                    
                except Exception as e:
                    logger.error(f"Error starting bot {bot_doc.get('_id')}: {e}")
                    continue
            
            logger.info(f"✅ Successfully started {len(self.bot_manager.active_bots)} bots")
            
        except Exception as e:
            logger.error(f"Error loading active bots: {e}")
    
    async def main_loop(self):
        """Main worker loop"""
        logger.info("🔄 Starting main worker loop...")
        
        iteration = 0
        
        while self.running:
            try:
                iteration += 1
                
                if iteration % 12 == 0:  # Every minute (5 sec * 12)
                    print()
                    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}Worker Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
                    print(f"Active Bots: {len(self.bot_manager.active_bots)}")
                    print(f"Iteration: {iteration}")
                    print()
                
                # Check for new bots to start
                await self.check_new_bots()
                
                # Check for bots to stop
                await self.check_stopped_bots()
                
                # Monitor active bots
                await self.monitor_bots()
                
                # Sleep for 5 seconds
                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                logger.info("Received shutdown signal")
                self.running = False
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)
        
        # Cleanup
        await self.shutdown()
    
    async def check_new_bots(self):
        """Check for new bots that need to be started"""
        try:
            # Find bots with status "running" that aren't in active_bots
            running_bots = list(self.db.db['bot_instances'].find({'status': 'running'}))
            
            for bot_doc in running_bots:
                bot_id = str(bot_doc['_id'])
                
                if bot_id not in self.bot_manager.active_bots:
                    user_id = bot_doc['user_id']
                    logger.info(f"Starting new bot {bot_id}")
                    
                    try:
                        await self.bot_manager.start_bot(user_id, bot_id)
                    except Exception as e:
                        logger.error(f"Error starting bot {bot_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error checking new bots: {e}")
    
    async def check_stopped_bots(self):
        """Check for bots that should be stopped"""
        try:
            # Get list of active bot IDs
            active_bot_ids = list(self.bot_manager.active_bots.keys())
            
            for bot_id in active_bot_ids:
                # Check if bot status is still "running" in database
                bot_doc = self.db.db['bot_instances'].find_one({'_id': bot_id})
                
                if not bot_doc or bot_doc.get('status') != 'running':
                    logger.info(f"Stopping bot {bot_id}")
                    
                    try:
                        bot = self.bot_manager.active_bots[bot_id]
                        await bot.stop()
                        del self.bot_manager.active_bots[bot_id]
                    except Exception as e:
                        logger.error(f"Error stopping bot {bot_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error checking stopped bots: {e}")
    
    async def monitor_bots(self):
        """Monitor active bots and log status"""
        try:
            for bot_id, bot in self.bot_manager.active_bots.items():
                try:
                    status = bot.get_status()
                    
                    # Log bot status periodically
                    if hasattr(bot, 'last_log_time'):
                        if (datetime.now() - bot.last_log_time).seconds > 300:  # Every 5 minutes
                            logger.info(f"Bot {bot_id}: {status}")
                            bot.last_log_time = datetime.now()
                    else:
                        bot.last_log_time = datetime.now()
                
                except Exception as e:
                    logger.error(f"Error monitoring bot {bot_id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in monitor_bots: {e}")
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down worker...")
        
        # Stop all active bots
        for bot_id in list(self.bot_manager.active_bots.keys()):
            try:
                await self.bot_manager.stop_bot(None, bot_id)
            except Exception as e:
                logger.error(f"Error stopping bot {bot_id}: {e}")
        
        logger.info("✅ Worker shutdown complete")


async def main():
    """Main entry point"""
    print(f"{Fore.GREEN}╔════════════════════════════════════════════════════════════════════╗{Style.RESET_ALL}")
    print(f"{Fore.GREEN}║                   TRADING BOT WORKER v2.0                          ║{Style.RESET_ALL}")
    print(f"{Fore.GREEN}║                   PRODUCTION MODE - REAL TRADING                   ║{Style.RESET_ALL}")
    print(f"{Fore.GREEN}╚════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}")
    print()
    print(f"{Fore.YELLOW}⚠️  WARNING: This worker executes REAL trades with REAL money!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️  Make sure all bots are properly configured before starting.{Style.RESET_ALL}")
    print()
    
    # Create and start worker
    worker = TradingBotWorker()
    await worker.start()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Worker stopped by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Worker error: {e}{Style.RESET_ALL}")
        raise
