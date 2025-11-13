"""
Admin Bot 24/7 Worker - Makes Money While You Sleep
Runs continuously, checks database for bot status, trades automatically
"""
import asyncio
import time
import logging
from datetime import datetime
from mongodb_database import MongoTradingDatabase
from admin_auto_trader import AdminAutoTrader
from colorama import Fore, Style
from bson import ObjectId

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdminBotWorker:
    """
    24/7 Worker that ensures admin bot is always running
    Monitors database for start/stop commands
    Restarts automatically if crashes
    """
    
    def __init__(self):
        self.db = MongoTradingDatabase()
        self.trader = None
        self.running = False
        logger.info(f"{Fore.GREEN}🤖 Admin Bot Worker initialized{Style.RESET_ALL}")
    
    def get_admin_user(self):
        """Get admin user from database"""
        try:
            admin = self.db.db['users'].find_one({"role": "admin"})
            return admin
        except Exception as e:
            logger.error(f"❌ Error fetching admin user: {e}")
            return None
    
    def should_bot_run(self, admin):
        """Check if bot should be running"""
        if not admin:
            return False
        return admin.get('new_listing_bot_enabled', False)
    
    def get_bot_config(self, admin):
        """Get bot configuration from database"""
        if not admin:
            return None
        return admin.get('new_listing_bot_config', {
            'buy_amount_usdt': 50,
            'take_profit_percent': 30,
            'stop_loss_percent': 15,
            'max_hold_time': 3600
        })
    
    async def start_bot(self, config):
        """Initialize and start the admin bot"""
        try:
            logger.info(f"{Fore.CYAN}🚀 Starting admin bot with config:{Style.RESET_ALL}")
            logger.info(f"   💰 Buy Amount: ${config.get('buy_amount_usdt', 50)}")
            logger.info(f"   📈 Take Profit: {config.get('take_profit_percent', 30)}%")
            logger.info(f"   📉 Stop Loss: {config.get('stop_loss_percent', 15)}%")
            logger.info(f"   ⏱️ Max Hold: {config.get('max_hold_time', 3600)}s")
            
            # Create trader instance
            self.trader = AdminAutoTrader()
            
            # Configure new listing bot
            self.trader.new_listing_bot.buy_amount_usdt = config.get('buy_amount_usdt', 50)
            self.trader.new_listing_bot.take_profit_percent = config.get('take_profit_percent', 30)
            self.trader.new_listing_bot.stop_loss_percent = config.get('stop_loss_percent', 15)
            self.trader.new_listing_bot.max_hold_time = config.get('max_hold_time', 3600)
            
            # Start new listing detection
            self.trader.run_new_listing_strategy()
            
            self.running = True
            logger.info(f"{Fore.GREEN}✅ Admin bot is now running!{Style.RESET_ALL}")
            logger.info(f"{Fore.YELLOW}💤 You can sleep now - I'll make you money!{Style.RESET_ALL}")
            
        except Exception as e:
            logger.error(f"❌ Error starting bot: {e}")
            self.trader = None
            self.running = False
    
    async def stop_bot(self):
        """Stop the admin bot"""
        try:
            logger.info(f"{Fore.YELLOW}⏹️ Stopping admin bot...{Style.RESET_ALL}")
            self.trader = None
            self.running = False
            logger.info("✅ Bot stopped")
        except Exception as e:
            logger.error(f"❌ Error stopping bot: {e}")
    
    async def monitor_bot(self):
        """Monitor bot and handle trades"""
        if not self.trader or not self.running:
            return
        
        try:
            # Get current balance
            balance = self.trader.get_current_balance()
            
            # Monitor positions
            self.trader.monitor_positions()
            
            # Run momentum strategy if balance is high enough
            if balance >= 50:
                self.trader.run_momentum_strategy(balance)
            
            logger.info(f"💰 Current balance: ${balance:.2f} | Positions: {len(self.trader.profit_protector.active_positions)}")
            
        except Exception as e:
            logger.error(f"❌ Error monitoring bot: {e}")
    
    async def update_config(self, new_config):
        """Update bot configuration on the fly"""
        if not self.trader:
            return
        
        try:
            logger.info(f"{Fore.CYAN}⚙️ Updating bot configuration...{Style.RESET_ALL}")
            
            self.trader.new_listing_bot.buy_amount_usdt = new_config.get('buy_amount_usdt', 50)
            self.trader.new_listing_bot.take_profit_percent = new_config.get('take_profit_percent', 30)
            self.trader.new_listing_bot.stop_loss_percent = new_config.get('stop_loss_percent', 15)
            self.trader.new_listing_bot.max_hold_time = new_config.get('max_hold_time', 3600)
            
            logger.info("✅ Configuration updated!")
            
        except Exception as e:
            logger.error(f"❌ Error updating config: {e}")
    
    async def run_forever(self):
        """
        Main worker loop
        Runs 24/7, checks database every 10 seconds
        Starts/stops bot based on database flags
        """
        logger.info(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        logger.info(f"{Fore.GREEN}🤖 ADMIN BOT 24/7 WORKER{Style.RESET_ALL}")
        logger.info(f"{Fore.GREEN}💰 Makes Money While You Sleep{Style.RESET_ALL}")
        logger.info(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
        
        last_config = None
        check_interval = 10  # Check database every 10 seconds
        monitor_interval = 60  # Monitor trades every 60 seconds
        last_monitor = time.time()
        
        while True:
            try:
                # Get admin user
                admin = self.get_admin_user()
                
                if not admin:
                    logger.warning("⚠️ No admin user found")
                    await asyncio.sleep(check_interval)
                    continue
                
                # Check if bot should run
                should_run = self.should_bot_run(admin)
                current_config = self.get_bot_config(admin)
                
                # Bot should start
                if should_run and not self.running:
                    await self.start_bot(current_config)
                    last_config = current_config
                
                # Bot should stop
                elif not should_run and self.running:
                    await self.stop_bot()
                    last_config = None
                
                # Configuration changed
                elif should_run and self.running and current_config != last_config:
                    await self.update_config(current_config)
                    last_config = current_config
                
                # Monitor bot (every 60 seconds)
                if self.running and (time.time() - last_monitor) >= monitor_interval:
                    await self.monitor_bot()
                    last_monitor = time.time()
                
                # Wait before next check
                await asyncio.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.info(f"{Fore.YELLOW}⏹️ Shutting down worker...{Style.RESET_ALL}")
                if self.running:
                    await self.stop_bot()
                break
                
            except Exception as e:
                logger.error(f"❌ Error in main loop: {e}")
                await asyncio.sleep(check_interval)
                # Try to restart bot if it crashed
                if self.running:
                    logger.warning("⚠️ Bot may have crashed, attempting restart...")
                    self.running = False
                    self.trader = None

async def main():
    """Entry point"""
    worker = AdminBotWorker()
    await worker.run_forever()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Worker stopped by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Worker crashed: {e}{Style.RESET_ALL}")
