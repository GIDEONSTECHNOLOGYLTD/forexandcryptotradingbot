"""
Telegram Bot for Trading Bot Pro
Sends notifications and alerts to users
"""
import os
import asyncio
from telegram import Bot
from telegram.error import TelegramError
import config
from mongodb_database import MongoTradingDatabase

class TelegramNotifier:
    """Send notifications via Telegram"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
        self.bot = None
        self.db = MongoTradingDatabase()
        
        if self.bot_token:
            self.bot = Bot(token=self.bot_token)
    
    async def send_message(self, chat_id: str, message: str):
        """Send a message to a specific chat"""
        if not self.bot:
            print("Telegram bot not configured")
            return False
        
        try:
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
            return True
        except TelegramError as e:
            print(f"Telegram error: {e}")
            return False
    
    async def notify_admin(self, message: str):
        """Send notification to admin"""
        if self.admin_chat_id:
            await self.send_message(self.admin_chat_id, f"🔔 <b>Admin Alert</b>\n\n{message}")
    
    async def notify_user(self, user_id: str, message: str):
        """Send notification to user"""
        # Get user's telegram chat ID from database
        user = self.db.db['users'].find_one({'_id': user_id})
        if user and user.get('telegram_chat_id'):
            await self.send_message(user['telegram_chat_id'], message)
    
    async def notify_new_user(self, email: str, full_name: str):
        """Notify admin of new user signup"""
        message = f"""
🎉 <b>New User Signup!</b>

👤 Name: {full_name}
📧 Email: {email}
🕐 Time: {asyncio.get_event_loop().time()}
"""
        await self.notify_admin(message)
    
    async def notify_new_subscription(self, email: str, plan: str, amount: float):
        """Notify admin of new subscription"""
        message = f"""
💰 <b>New Subscription!</b>

👤 User: {email}
📦 Plan: {plan.upper()}
💵 Amount: ${amount}
🕐 Time: {asyncio.get_event_loop().time()}
"""
        await self.notify_admin(message)
    
    async def notify_bot_created(self, user_email: str, bot_type: str, symbol: str, capital: float):
        """Notify admin when user creates a bot"""
        message = f"""
🤖 <b>New Bot Created!</b>

👤 User: {user_email}
🔧 Type: {bot_type}
📊 Symbol: {symbol}
💰 Capital: ${capital}
"""
        await self.notify_admin(message)
    
    async def notify_trade_executed(self, user_id: str, symbol: str, side: str, amount: float, price: float):
        """Notify user of trade execution"""
        message = f"""
✅ <b>Trade Executed!</b>

📊 Symbol: {symbol}
📈 Side: {side.upper()}
💰 Amount: {amount}
💵 Price: ${price}
📍 Total: ${amount * price}
"""
        await self.notify_user(user_id, message)
        
        # Also notify admin
        user = self.db.db['users'].find_one({'_id': user_id})
        admin_msg = f"""
💹 <b>Trade Alert!</b>

👤 User: {user.get('email', 'Unknown')}
📊 {symbol} {side.upper()}
💰 Amount: {amount} @ ${price}
"""
        await self.notify_admin(admin_msg)
    
    async def notify_bot_stopped(self, user_id: str, bot_type: str, reason: str = "Manual stop"):
        """Notify user when bot stops"""
        message = f"""
⏸️ <b>Bot Stopped</b>

🤖 Type: {bot_type}
📝 Reason: {reason}
"""
        await self.notify_user(user_id, message)
    
    async def notify_error(self, user_id: str, error_message: str):
        """Notify user of errors"""
        message = f"""
⚠️ <b>Error Alert</b>

{error_message}

Please check your bot configuration.
"""
        await self.notify_user(user_id, message)
        await self.notify_admin(f"Error for user {user_id}: {error_message}")

# Singleton instance
telegram_notifier = TelegramNotifier()

# Helper functions for easy use
async def notify_admin(message: str):
    """Quick function to notify admin"""
    await telegram_notifier.notify_admin(message)

async def notify_user(user_id: str, message: str):
    """Quick function to notify user"""
    await telegram_notifier.notify_user(user_id, message)

async def notify_new_signup(email: str, full_name: str):
    """Quick function for new signup"""
    await telegram_notifier.notify_new_user(email, full_name)

async def notify_subscription(email: str, plan: str, amount: float):
    """Quick function for new subscription"""
    await telegram_notifier.notify_new_subscription(email, plan, amount)
