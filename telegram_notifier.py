"""
Telegram Notifications
Send real-time alerts about trades, performance, and errors
"""
import requests
import os
import time
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
        
        # Rate limiting: Track last message time
        self.last_message_time = 0
        self.min_message_interval = 0.1  # 100ms between messages (max 10/second)
        
        # DEBUG: Show what we're getting
        print(f"{Fore.CYAN}🔍 Telegram Config Debug:{Style.RESET_ALL}")
        print(f"  Bot Token: {'✅ Found' if self.bot_token else '❌ Missing'} {f'({self.bot_token[:10]}...)' if self.bot_token else ''}")
        print(f"  Chat ID: {'✅ Found' if self.chat_id else '❌ Missing'} {f'({self.chat_id})' if self.chat_id else ''}")
        
        if not self.enabled:
            print(f"{Fore.YELLOW}⚠️  Telegram notifications disabled (no credentials){Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Telegram notifications enabled{Style.RESET_ALL}")
    
    def send_message(self, message, parse_mode='HTML', max_retries=3):
        """
        Send a message to Telegram with retry logic and rate limiting
        
        Args:
            message: The message to send
            parse_mode: HTML or Markdown
            max_retries: Number of retry attempts if send fails
        
        Returns:
            bool: True if message was sent successfully
        """
        if not self.enabled:
            return False
        
        # Rate limiting: Wait if we're sending too fast
        current_time = time.time()
        time_since_last = current_time - self.last_message_time
        if time_since_last < self.min_message_interval:
            wait_time = self.min_message_interval - time_since_last
            time.sleep(wait_time)
        
        # Try sending with retries
        for attempt in range(max_retries):
            try:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': parse_mode
                }
                
                response = requests.post(url, data=data, timeout=10)
                self.last_message_time = time.time()
                
                if response.status_code == 200:
                    return True
                elif response.status_code == 429:  # Rate limit hit
                    # Telegram told us to slow down
                    retry_after = response.json().get('parameters', {}).get('retry_after', 1)
                    print(f"{Fore.YELLOW}⚠️ Telegram rate limit hit, waiting {retry_after}s{Style.RESET_ALL}")
                    time.sleep(retry_after)
                    continue
                else:
                    # Any other error code (500, 503, etc.) - retry
                    print(f"{Fore.RED}❌ Telegram error (status {response.status_code}, attempt {attempt + 1}/{max_retries}): {response.text}{Style.RESET_ALL}")
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Wait before retry
                        continue
                    # Last attempt failed, fall through to return False
                    
            except requests.exceptions.Timeout:
                print(f"{Fore.YELLOW}⚠️ Telegram timeout (attempt {attempt + 1}/{max_retries}){Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # Wait 1 second before retry
                    continue
            except Exception as e:
                print(f"{Fore.RED}❌ Telegram error (attempt {attempt + 1}/{max_retries}): {e}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
        
        # All retries failed
        print(f"{Fore.RED}❌ Failed to send Telegram message after {max_retries} attempts{Style.RESET_ALL}")
        return False
    
    def send_trade_alert(self, trade_data):
        """Send trade execution alert"""
        symbol = trade_data.get('symbol', 'UNKNOWN')
        side = trade_data.get('side', 'buy').upper()
        price = trade_data.get('entry_price', 0)
        amount = trade_data.get('amount', 0)
        confidence = trade_data.get('confidence', 0)
        stop_loss = trade_data.get('stop_loss', 0)
        take_profit = trade_data.get('take_profit', 0)
        
        # 🔧 FIX: Validate critical fields before sending
        if price <= 0:
            # Don't send notification if price is invalid
            print(f"⚠️ Cannot send trade alert - invalid price: ${price}")
            return False
        
        # Emoji based on side
        emoji = "🟢" if side == "BUY" else "🔴"
        
        # Build message with proper formatting
        message = f"""
{emoji} <b>TRADE EXECUTED</b>

<b>Symbol:</b> {symbol}
<b>Side:</b> {side}
<b>Price:</b> ${price:,.6f}
<b>Amount:</b> {amount:.6f}
<b>Confidence:</b> {confidence:.1f}%
"""
        
        # Only add stop loss and take profit if they're valid
        if stop_loss > 0:
            message += f"\n<b>Stop Loss:</b> ${stop_loss:,.6f}"
        else:
            message += f"\n<b>Stop Loss:</b> ⚠️ Not set"
            
        if take_profit > 0:
            message += f"\n<b>Take Profit:</b> ${take_profit:,.6f}"
        else:
            message += f"\n<b>Take Profit:</b> ⚠️ Not set"
        
        message += f"\n\n<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>\n"
        
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
    
    # ============================================================================
    # COMPREHENSIVE NOTIFICATION METHODS - COVERS EVERYTHING!
    # ============================================================================
    
    def send_small_win(self, symbol, entry, exit, profit_usd, profit_pct, total_small_wins, accumulated_profit):
        """Notify about small win (5% auto-exit)"""
        message = f"""
💎 <b>SMALL WIN - AUTO EXIT!</b>

🪙 Symbol: <b>{symbol}</b>
📈 Entry: ${entry:.6f}
📊 Exit: ${exit:.6f}
💰 Profit: <b>+${profit_usd:.2f} (+{profit_pct:.1f}%)</b>

✅ Quick profit secured!
🎯 Total small wins: {total_small_wins}
💎 Accumulated: ${accumulated_profit:.2f}

💡 Many small wins = Big total profit!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_partial_profit(self, symbol, percent_sold, profit_usd, profit_pct, remaining_amount):
        """Notify about partial profit taking"""
        message = f"""
💰 <b>PARTIAL PROFIT TAKEN</b>

🪙 Symbol: <b>{symbol}</b>
📤 Sold: {percent_sold}% of position
💵 Profit: <b>+${profit_usd:.2f} (+{profit_pct:.1f}%)</b>

📊 Remaining: {remaining_amount:.6f}
🎯 Letting rest ride for more profit!

✅ Profits locked in, risk reduced!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_trailing_stop_hit(self, symbol, entry, peak, exit, profit_usd, profit_pct):
        """Notify about trailing stop exit"""
        message = f"""
📉 <b>TRAILING STOP HIT</b>

🪙 Symbol: <b>{symbol}</b>
📈 Entry: ${entry:.6f}
🔝 Peak: ${peak:.6f} (highest price)
📊 Exit: ${exit:.6f}
💰 Profit: <b>+${profit_usd:.2f} (+{profit_pct:.1f}%)</b>

✅ Locked in most gains!
🛡️ Protected your profits!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_stop_loss_hit(self, symbol, entry, exit, loss_usd, loss_pct):
        """Notify about stop loss hit"""
        message = f"""
🛑 <b>STOP LOSS HIT</b>

🪙 Symbol: <b>{symbol}</b>
📈 Entry: ${entry:.6f}
📊 Exit: ${exit:.6f}
💸 Loss: <b>${loss_usd:.2f} ({loss_pct:.1f}%)</b>

✅ Loss limited by stop loss!
🛡️ Protected from bigger loss!

💡 This is normal - we win more than we lose!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_break_even_activated(self, symbol, entry_price, current_price, profit_pct):
        """Notify about break-even protection activated"""
        message = f"""
🎯 <b>BREAK-EVEN PROTECTION ACTIVATED!</b>

🪙 Symbol: <b>{symbol}</b>
📈 Entry: ${entry_price:.6f}
📊 Current: ${current_price:.6f}
📈 Profit: <b>+{profit_pct:.1f}%</b>

🛡️ Stop loss moved to entry price!
✅ This trade is now RISK-FREE!
💰 Can only profit or break even!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_consecutive_losses_warning(self, losses_count, pause_duration_mins):
        """Notify about consecutive losses pause"""
        message = f"""
⚠️ <b>CONSECUTIVE LOSS LIMIT</b>

📉 Losses in a row: <b>{losses_count}</b>

🛑 Pausing trading for {pause_duration_mins} minutes
⏰ Resumes at: {(datetime.now()).strftime('%H:%M UTC')}

💡 <b>Why?</b>
Market conditions may be unfavorable.
Taking a break prevents further losses.

✅ Your capital is PROTECTED!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_daily_limit_reached(self, loss_pct, starting_balance, current_balance, loss_amount):
        """Notify about daily loss limit reached"""
        message = f"""
🚨 <b>DAILY LOSS LIMIT REACHED!</b>

📉 Lost: <b>{abs(loss_pct):.2f}% today</b>
💰 Starting: ${starting_balance:.2f}
💵 Current: ${current_balance:.2f}
💸 Loss: ${abs(loss_amount):.2f}

🛑 <b>TRADING PAUSED UNTIL TOMORROW!</b>
⏰ Resumes: Tomorrow 00:00 UTC

💡 <b>Why?</b>
Protecting you from bigger losses.
Market will be better tomorrow.

✅ Maximum protection activated!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_balance_update(self, previous_balance, current_balance, change_pct):
        """Notify about significant balance changes"""
        emoji = "📈" if change_pct > 0 else "📉"
        direction = "UP" if change_pct > 0 else "DOWN"
        
        message = f"""
{emoji} <b>BALANCE UPDATE</b>

💰 Previous: ${previous_balance:.2f}
💵 Current: ${current_balance:.2f}
📊 Change: <b>{change_pct:+.2f}%</b>

{emoji} Account is {direction} {abs(change_pct):.2f}%!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_new_listing_alert(self, symbol, price, volume_24h):
        """Notify about new listing detected"""
        message = f"""
🆕 <b>NEW LISTING DETECTED!</b>

🪙 Symbol: <b>{symbol}</b>
💰 Price: ${price:.6f}
📊 24h Volume: ${volume_24h:,.0f}

🚀 New listing bot is analyzing...
⚡ May enter position if conditions are good!

💡 New listings can be very profitable!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_api_error(self, error_type, error_message, retry_count=0):
        """Notify about API errors"""
        message = f"""
⚠️ <b>API ERROR</b>

🔴 Type: {error_type}
📝 Error: {error_message}
🔄 Retries: {retry_count}

💡 Bot is handling this automatically.
No action needed from you.

✅ Trading will continue once resolved.

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_order_failed(self, symbol, side, amount, reason):
        """Notify about failed orders"""
        message = f"""
🚨 <b>ORDER FAILED</b>

🪙 Symbol: {symbol}
📊 Side: {side}
💰 Amount: {amount:.6f}
❌ Reason: {reason}

🔄 Bot will retry or skip this trade.
💡 This happens sometimes, it's normal.

✅ No money lost, order wasn't executed.

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_profit_milestone(self, milestone_pct, total_profit, starting_capital, current_capital):
        """Notify about profit milestones (10%, 20%, 50%, etc)"""
        message = f"""
🎉 <b>PROFIT MILESTONE REACHED!</b>

🏆 Total Profit: <b>{milestone_pct}%</b>
💰 Starting Capital: ${starting_capital:.2f}
💵 Current Capital: ${current_capital:.2f}
💎 Total Profit: <b>${total_profit:.2f}</b>

🚀 Your account is growing!
📈 Keep going, compound effect is real!

🎯 Next milestone: {milestone_pct + 10}%

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_emergency_exit(self, symbol, reason, entry, exit, pnl_pct):
        """Notify about emergency exits"""
        message = f"""
🚨 <b>EMERGENCY EXIT!</b>

🪙 Symbol: <b>{symbol}</b>
⚠️ Reason: {reason}
📈 Entry: ${entry:.6f}
📊 Exit: ${exit:.6f}
📉 Change: {pnl_pct:+.2f}%

🛡️ <b>Emergency protection activated!</b>
✅ Bot detected dangerous condition
💡 Better safe than sorry!

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_weekly_summary(self, stats):
        """Send weekly performance summary"""
        total_trades = stats.get('total_trades', 0)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        win_rate = stats.get('win_rate', 0)
        weekly_pnl = stats.get('weekly_pnl', 0)
        best_trade = stats.get('best_trade', 0)
        worst_trade = stats.get('worst_trade', 0)
        starting_capital = stats.get('starting_capital', 0)
        current_capital = stats.get('current_capital', 0)
        
        emoji = "📈" if weekly_pnl > 0 else "📉"
        
        message = f"""
{emoji} <b>WEEKLY SUMMARY</b>

💰 Starting: ${starting_capital:.2f}
💵 Current: ${current_capital:.2f}
📊 Weekly P&L: <b>{weekly_pnl:+.2f} USD ({((current_capital - starting_capital) / starting_capital * 100):+.1f}%)</b>

📈 Trades: {total_trades}
✅ Wins: {wins}
❌ Losses: {losses}
🎯 Win Rate: <b>{win_rate:.1f}%</b>

🏆 Best Trade: +${best_trade:.2f}
📉 Worst Trade: ${worst_trade:.2f}

{"🚀 Great week! Keep it up!" if weekly_pnl > 0 else "💪 Stay strong! Next week will be better!"}

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_config_warning(self, warning_message):
        """Notify about configuration warnings"""
        message = f"""
⚠️ <b>CONFIG WARNING</b>

{warning_message}

💡 Bot auto-corrected to safe defaults.
✅ Everything is working safely.

📝 Check your settings if needed.

<i>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)
    
    def send_ai_suggestion(self, symbol, current_pnl_pct, current_pnl_usd, reason, suggestion):
        """Send AI-powered trade suggestions"""
        message = f"""
🤖 <b>AI SUGGESTION</b>

🪙 Symbol: <b>{symbol}</b>
📈 Current Profit: <b>+${current_pnl_usd:.2f} (+{current_pnl_pct:.1f}%)</b>

💡 <b>{reason}</b>

✅ Suggestion: {suggestion}

🎯 <b>Your decision!</b>
Bot will execute automatically based on your settings.

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
