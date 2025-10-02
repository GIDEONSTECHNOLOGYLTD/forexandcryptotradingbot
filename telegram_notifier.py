"""
Telegram Notifications
Send real-time alerts about trades, performance, and errors
"""
import requests
import os
from datetime import datetime
from colorama import Fore, Style


class TelegramNotifier:
    def __init__(self, bot_token=None, chat_id=None):
        """
        Initialize Telegram notifier
        
        Get your bot token from @BotFather on Telegram
        Get your chat_id by messaging your bot and visiting:
        https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
        """
        self.bot_token = bot_token or os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = chat_id or os.getenv('TELEGRAM_CHAT_ID')
        self.enabled = bool(self.bot_token and self.chat_id)
        
        if not self.enabled:
            print(f"{Fore.YELLOW}⚠️  Telegram notifications disabled (no credentials){Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Telegram notifications enabled{Style.RESET_ALL}")
    
    def send_message(self, message, parse_mode='HTML'):
        """Send a message to Telegram"""
        if not self.enabled:
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
            
        except Exception as e:
            print(f"{Fore.RED}❌ Telegram error: {e}{Style.RESET_ALL}")
            return False
    
    def send_trade_alert(self, trade_data):
        """Send trade execution alert"""
        symbol = trade_data['symbol']
        side = trade_data['side'].upper()
        price = trade_data['entry_price']
        amount = trade_data['amount']
        confidence = trade_data.get('confidence', 0)
        stop_loss = trade_data.get('stop_loss', 0)
        take_profit = trade_data.get('take_profit', 0)
        
        # Emoji based on side
        emoji = "🟢" if side == "BUY" else "🔴"
        
        message = f"""
{emoji} <b>TRADE EXECUTED</b>

<b>Symbol:</b> {symbol}
<b>Side:</b> {side}
<b>Price:</b> ${price:,.2f}
<b>Amount:</b> {amount:.6f}
<b>Confidence:</b> {confidence:.1f}%

<b>Stop Loss:</b> ${stop_loss:,.2f}
<b>Take Profit:</b> ${take_profit:,.2f}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_position_closed(self, trade_record):
        """Send position closed alert"""
        symbol = trade_record['symbol']
        entry = trade_record['entry_price']
        exit_price = trade_record['exit_price']
        pnl = trade_record['pnl']
        pnl_percent = trade_record['pnl_percent']
        reason = trade_record.get('exit_reason', 'manual')
        
        # Emoji based on profit/loss
        emoji = "✅" if pnl > 0 else "❌"
        
        message = f"""
{emoji} <b>POSITION CLOSED</b>

<b>Symbol:</b> {symbol}
<b>Entry:</b> ${entry:,.2f}
<b>Exit:</b> ${exit_price:,.2f}
<b>Reason:</b> {reason.upper()}

<b>PnL:</b> ${pnl:,.2f} ({pnl_percent:+.2f}%)

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_daily_summary(self, stats):
        """Send daily performance summary"""
        total_pnl = stats['total_pnl']
        daily_pnl = stats.get('daily_pnl', 0)
        win_rate = stats['win_rate']
        total_trades = stats['total_trades']
        current_capital = stats['current_capital']
        
        emoji = "📈" if daily_pnl >= 0 else "📉"
        
        message = f"""
{emoji} <b>DAILY SUMMARY</b>

<b>Current Capital:</b> ${current_capital:,.2f}
<b>Daily PnL:</b> ${daily_pnl:,.2f}
<b>Total PnL:</b> ${total_pnl:,.2f}

<b>Total Trades:</b> {total_trades}
<b>Win Rate:</b> {win_rate:.1f}%

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_error_alert(self, error_message):
        """Send error alert"""
        message = f"""
🚨 <b>ERROR ALERT</b>

<b>Error:</b> {error_message}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_signal_alert(self, symbol, signal, confidence, price):
        """Send trading signal alert"""
        emoji = "🔔"
        
        message = f"""
{emoji} <b>SIGNAL DETECTED</b>

<b>Symbol:</b> {symbol}
<b>Signal:</b> {signal.upper()}
<b>Confidence:</b> {confidence:.1f}%
<b>Price:</b> ${price:,.2f}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_bot_started(self):
        """Send bot started notification"""
        message = f"""
🤖 <b>BOT STARTED</b>

Trading bot is now running and monitoring markets.

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_bot_stopped(self):
        """Send bot stopped notification"""
        message = f"""
🛑 <b>BOT STOPPED</b>

Trading bot has been stopped.

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_daily_loss_limit(self, loss_percent):
        """Send daily loss limit alert"""
        message = f"""
⚠️ <b>DAILY LOSS LIMIT REACHED</b>

Daily loss has exceeded {loss_percent:.1f}%.
Bot has stopped trading for today.

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)
    
    def send_custom_alert(self, title, body):
        """Send custom alert"""
        message = f"""
📢 <b>{title}</b>

{body}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        
        return self.send_message(message)


# Example usage and setup guide
if __name__ == "__main__":
    print(f"{Fore.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║              TELEGRAM NOTIFICATIONS SETUP GUIDE                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Style.RESET_ALL}\n")
    
    print(f"{Fore.YELLOW}Step 1: Create a Telegram Bot{Style.RESET_ALL}")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Follow instructions to create your bot")
    print("4. Copy the bot token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    
    print(f"\n{Fore.YELLOW}Step 2: Get Your Chat ID{Style.RESET_ALL}")
    print("1. Start a chat with your bot")
    print("2. Send any message to your bot")
    print("3. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("4. Find your chat_id in the response (looks like: 123456789)")
    
    print(f"\n{Fore.YELLOW}Step 3: Add to .env File{Style.RESET_ALL}")
    print("Add these lines to your .env file:")
    print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
    print("TELEGRAM_CHAT_ID=your_chat_id_here")
    
    print(f"\n{Fore.YELLOW}Step 4: Test Notifications{Style.RESET_ALL}")
    print("Run this file to test: python telegram_notifier.py")
    
    # Test if credentials are available
    notifier = TelegramNotifier()
    
    if notifier.enabled:
        print(f"\n{Fore.GREEN}✅ Testing notifications...{Style.RESET_ALL}")
        
        # Test message
        success = notifier.send_custom_alert(
            "Test Alert",
            "If you receive this, Telegram notifications are working! 🎉"
        )
        
        if success:
            print(f"{Fore.GREEN}✅ Test message sent successfully!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ Failed to send test message{Style.RESET_ALL}")
    else:
        print(f"\n{Fore.YELLOW}⚠️  Please configure Telegram credentials in .env{Style.RESET_ALL}")
