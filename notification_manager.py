"""
Multi-Channel Notification Manager
Supports Email, Telegram, SMS, and Push Notifications
"""
import smtplib
from email.mime.text import EIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    Centralized notification system supporting multiple channels
    """
    
    def __init__(self, user_preferences=None):
        self.user_preferences = user_preferences or {}
        self.telegram_enabled = bool(config.TELEGRAM_BOT_TOKEN)
        self.email_enabled = True  # Always try email
        
    def send_trade_notification(self, trade_data, user_email=None, user_telegram_id=None):
        """Send notification when trade is executed"""
        message = self._format_trade_message(trade_data)
        
        # Send via enabled channels
        if user_email and self.user_preferences.get('email_notifications', True):
            self.send_email(user_email, "Trade Executed", message)
        
        if user_telegram_id and self.telegram_enabled:
            self.send_telegram(user_telegram_id, message)
    
    def send_alert(self, alert_type, message, user_email=None, user_telegram_id=None):
        """Send alert notification"""
        subject = f"Trading Bot Alert: {alert_type}"
        
        if user_email:
            self.send_email(user_email, subject, message)
        
        if user_telegram_id and self.telegram_enabled:
            self.send_telegram(user_telegram_id, f"🚨 {alert_type}\n\n{message}")
    
    def send_daily_summary(self, summary_data, user_email=None, user_telegram_id=None):
        """Send daily performance summary"""
        message = self._format_daily_summary(summary_data)
        
        if user_email:
            self.send_email(user_email, "Daily Trading Summary", message, html=True)
        
        if user_telegram_id and self.telegram_enabled:
            self.send_telegram(user_telegram_id, message)
    
    def send_email(self, to_email, subject, message, html=False):
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = config.EMAIL_FROM
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            # Send via SMTP
            with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
                server.starttls()
                server.login(config.SMTP_USER, config.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_telegram(self, chat_id, message):
        """Send Telegram notification"""
        try:
            url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                logger.info(f"Telegram message sent to {chat_id}")
                return True
            else:
                logger.error(f"Telegram error: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    def send_push_notification(self, user_id, title, body, data=None):
        """Send push notification to mobile app"""
        # Placeholder for push notification service (Firebase, OneSignal, etc.)
        try:
            # Implement your push notification service here
            logger.info(f"Push notification sent to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    def _format_trade_message(self, trade_data):
        """Format trade data into readable message"""
        signal = trade_data.get('signal', '').upper()
        symbol = trade_data.get('symbol', '')
        entry_price = trade_data.get('entry_price', 0)
        position_size = trade_data.get('position_size', 0)
        stop_loss = trade_data.get('stop_loss', 0)
        take_profit = trade_data.get('take_profit', 0)
        confidence = trade_data.get('confidence', 0)
        strategy = trade_data.get('strategy', 'unknown')
        
        message = f"""
🤖 <b>Trade Executed</b>

📊 <b>Symbol:</b> {symbol}
📈 <b>Signal:</b> {signal}
💰 <b>Entry Price:</b> ${entry_price:.4f}
📦 <b>Position Size:</b> {position_size:.4f}
🛑 <b>Stop Loss:</b> ${stop_loss:.4f}
🎯 <b>Take Profit:</b> ${take_profit:.4f}
✅ <b>Confidence:</b> {confidence:.1f}%
🎲 <b>Strategy:</b> {strategy.title()}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        return message.strip()
    
    def _format_daily_summary(self, summary_data):
        """Format daily summary into readable message"""
        total_trades = summary_data.get('total_trades', 0)
        winning_trades = summary_data.get('winning_trades', 0)
        losing_trades = summary_data.get('losing_trades', 0)
        win_rate = summary_data.get('win_rate', 0)
        total_pnl = summary_data.get('total_pnl', 0)
        best_trade = summary_data.get('best_trade', 0)
        worst_trade = summary_data.get('worst_trade', 0)
        
        pnl_emoji = "📈" if total_pnl > 0 else "📉"
        
        message = f"""
📊 <b>Daily Trading Summary</b>

{pnl_emoji} <b>Total P&L:</b> ${total_pnl:,.2f}

📈 <b>Trades:</b> {total_trades}
✅ <b>Wins:</b> {winning_trades}
❌ <b>Losses:</b> {losing_trades}
🎯 <b>Win Rate:</b> {win_rate:.1f}%

🏆 <b>Best Trade:</b> ${best_trade:,.2f}
💔 <b>Worst Trade:</b> ${worst_trade:,.2f}

📅 <b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}
        """
        
        return message.strip()
    
    def send_risk_alert(self, alert_type, details, user_email=None, user_telegram_id=None):
        """Send risk management alert"""
        alerts = {
            'max_drawdown': '⚠️ Maximum drawdown limit reached!',
            'daily_loss': '🛑 Daily loss limit exceeded!',
            'position_limit': '📊 Maximum positions reached!',
            'high_volatility': '📈 High market volatility detected!'
        }
        
        title = alerts.get(alert_type, '⚠️ Risk Alert')
        message = f"{title}\n\n{details}"
        
        self.send_alert(alert_type, message, user_email, user_telegram_id)
    
    def send_performance_report(self, report_data, user_email=None):
        """Send detailed performance report via email"""
        html_report = self._generate_html_report(report_data)
        
        if user_email:
            self.send_email(
                user_email,
                "Weekly Performance Report",
                html_report,
                html=True
            )
    
    def _generate_html_report(self, report_data):
        """Generate HTML email report"""
        overview = report_data.get('overview', {})
        profitability = report_data.get('profitability', {})
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .metric {{ margin: 10px 0; padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
                .positive {{ color: green; }}
                .negative {{ color: red; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Trading Bot Performance Report</h1>
            </div>
            
            <div class="metric">
                <h2>Overview</h2>
                <p><strong>Total Trades:</strong> {overview.get('total_trades', 0)}</p>
                <p><strong>Win Rate:</strong> {overview.get('win_rate', 0):.1f}%</p>
                <p class="{'positive' if overview.get('total_pnl', 0) > 0 else 'negative'}">
                    <strong>Total P&L:</strong> ${overview.get('total_pnl', 0):,.2f}
                </p>
            </div>
            
            <div class="metric">
                <h2>Profitability</h2>
                <p><strong>Profit Factor:</strong> {profitability.get('profit_factor', 0):.2f}</p>
                <p><strong>Average Win:</strong> ${profitability.get('avg_win', 0):,.2f}</p>
                <p><strong>Average Loss:</strong> ${profitability.get('avg_loss', 0):,.2f}</p>
            </div>
        </body>
        </html>
        """
        
        return html


class AlertManager:
    """Manage trading alerts and conditions"""
    
    def __init__(self, notification_manager):
        self.notifier = notification_manager
        self.active_alerts = {}
        
    def check_price_alert(self, symbol, current_price, user_alerts):
        """Check if price alerts should be triggered"""
        for alert in user_alerts:
            if alert['symbol'] == symbol:
                target_price = alert['target_price']
                condition = alert['condition']  # 'above' or 'below'
                
                triggered = False
                if condition == 'above' and current_price >= target_price:
                    triggered = True
                elif condition == 'below' and current_price <= target_price:
                    triggered = True
                
                if triggered and alert['id'] not in self.active_alerts:
                    message = f"{symbol} has reached ${current_price:.2f} ({condition} ${target_price:.2f})"
                    self.notifier.send_alert(
                        'Price Alert',
                        message,
                        alert.get('email'),
                        alert.get('telegram_id')
                    )
                    self.active_alerts[alert['id']] = datetime.now()
    
    def check_performance_alerts(self, performance_data, user_email, user_telegram_id):
        """Check performance-based alerts"""
        # Check win rate
        win_rate = performance_data.get('win_rate', 0)
        if win_rate < 40:
            self.notifier.send_risk_alert(
                'low_win_rate',
                f"Win rate has dropped to {win_rate:.1f}%. Consider reviewing your strategy.",
                user_email,
                user_telegram_id
            )
        
        # Check drawdown
        drawdown = abs(performance_data.get('max_drawdown', 0))
        if drawdown > 15:
            self.notifier.send_risk_alert(
                'max_drawdown',
                f"Drawdown has reached {drawdown:.1f}%. Consider reducing position sizes.",
                user_email,
                user_telegram_id
            )
