"""
Mobile Push Notifications
Expo Push Notifications for React Native app
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Handle mobile push notifications via Expo
    """
    
    EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
    
    def __init__(self):
        """Initialize push notification service"""
        self.expo_access_token = os.getenv('EXPO_ACCESS_TOKEN', '')
        
    def send_notification(
        self,
        push_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
        sound: str = 'default',
        badge: Optional[int] = None,
        priority: str = 'high'
    ) -> Dict:
        """
        Send push notification to a single device
        
        Args:
            push_token: Expo push token
            title: Notification title
            body: Notification body
            data: Additional data payload
            sound: Notification sound
            badge: Badge count
            priority: Notification priority (default, normal, high)
            
        Returns:
            Response from Expo push service
        """
        try:
            # Validate push token format
            if not push_token.startswith('ExponentPushToken['):
                logger.warning(f"Invalid push token format: {push_token}")
                return {'status': 'error', 'message': 'Invalid push token format'}
            
            # Prepare notification payload
            payload = {
                'to': push_token,
                'title': title,
                'body': body,
                'sound': sound,
                'priority': priority,
                'data': data or {}
            }
            
            if badge is not None:
                payload['badge'] = badge
            
            # Send notification
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            
            if self.expo_access_token:
                headers['Authorization'] = f'Bearer {self.expo_access_token}'
            
            response = requests.post(
                self.EXPO_PUSH_URL,
                json=payload,
                headers=headers
            )
            
            result = response.json()
            
            if response.status_code == 200:
                logger.info(f"✅ Push notification sent to {push_token[:20]}...")
                return {'status': 'success', 'data': result}
            else:
                logger.error(f"❌ Push notification failed: {result}")
                return {'status': 'error', 'message': result}
                
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def send_batch_notifications(
        self,
        notifications: List[Dict]
    ) -> Dict:
        """
        Send multiple push notifications in batch
        
        Args:
            notifications: List of notification dicts with 'to', 'title', 'body', etc.
            
        Returns:
            Batch response from Expo
        """
        try:
            if not notifications:
                return {'status': 'error', 'message': 'No notifications to send'}
            
            # Prepare batch payload
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            
            if self.expo_access_token:
                headers['Authorization'] = f'Bearer {self.expo_access_token}'
            
            response = requests.post(
                self.EXPO_PUSH_URL,
                json=notifications,
                headers=headers
            )
            
            result = response.json()
            
            if response.status_code == 200:
                logger.info(f"✅ Batch notifications sent: {len(notifications)} messages")
                return {'status': 'success', 'data': result}
            else:
                logger.error(f"❌ Batch notifications failed: {result}")
                return {'status': 'error', 'message': result}
                
        except Exception as e:
            logger.error(f"Error sending batch notifications: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def send_trade_notification(
        self,
        push_token: str,
        trade_type: str,
        symbol: str,
        price: float,
        amount: float,
        pnl: Optional[float] = None
    ) -> Dict:
        """
        Send trade-specific notification
        
        Args:
            push_token: User's push token
            trade_type: 'buy', 'sell', 'closed'
            symbol: Trading pair
            price: Trade price
            amount: Trade amount
            pnl: Profit/loss (for closed trades)
            
        Returns:
            Notification response
        """
        if trade_type == 'buy':
            title = f"🟢 Buy Order Executed"
            body = f"Bought {amount} {symbol} at ${price:.2f}"
            emoji = "🟢"
        elif trade_type == 'sell':
            title = f"🔴 Sell Order Executed"
            body = f"Sold {amount} {symbol} at ${price:.2f}"
            emoji = "🔴"
        elif trade_type == 'closed':
            pnl_emoji = "💚" if pnl and pnl > 0 else "❤️"
            title = f"{pnl_emoji} Position Closed"
            body = f"{symbol}: P&L ${pnl:.2f}" if pnl else f"{symbol} position closed"
            emoji = pnl_emoji
        else:
            title = "Trade Update"
            body = f"{trade_type} {symbol}"
            emoji = "📊"
        
        data = {
            'type': 'trade',
            'trade_type': trade_type,
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'pnl': pnl,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.send_notification(
            push_token=push_token,
            title=title,
            body=body,
            data=data,
            sound='default',
            priority='high'
        )
    
    def send_bot_status_notification(
        self,
        push_token: str,
        bot_name: str,
        status: str,
        message: Optional[str] = None
    ) -> Dict:
        """
        Send bot status notification
        
        Args:
            push_token: User's push token
            bot_name: Bot identifier
            status: 'started', 'stopped', 'error'
            message: Additional message
            
        Returns:
            Notification response
        """
        if status == 'started':
            title = "🚀 Bot Started"
            body = f"{bot_name} is now running"
            emoji = "🚀"
        elif status == 'stopped':
            title = "⏸️ Bot Stopped"
            body = f"{bot_name} has been stopped"
            emoji = "⏸️"
        elif status == 'error':
            title = "⚠️ Bot Error"
            body = f"{bot_name}: {message or 'An error occurred'}"
            emoji = "⚠️"
        else:
            title = "Bot Update"
            body = f"{bot_name}: {status}"
            emoji = "🤖"
        
        data = {
            'type': 'bot_status',
            'bot_name': bot_name,
            'status': status,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.send_notification(
            push_token=push_token,
            title=title,
            body=body,
            data=data,
            sound='default'
        )
    
    def send_alert_notification(
        self,
        push_token: str,
        alert_type: str,
        message: str,
        priority: str = 'high'
    ) -> Dict:
        """
        Send alert notification
        
        Args:
            push_token: User's push token
            alert_type: 'price', 'risk', 'system', etc.
            message: Alert message
            priority: Notification priority
            
        Returns:
            Notification response
        """
        emoji_map = {
            'price': '💰',
            'risk': '⚠️',
            'system': '🔔',
            'profit': '💚',
            'loss': '❤️',
            'info': 'ℹ️'
        }
        
        emoji = emoji_map.get(alert_type, '🔔')
        title = f"{emoji} Alert: {alert_type.title()}"
        
        data = {
            'type': 'alert',
            'alert_type': alert_type,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.send_notification(
            push_token=push_token,
            title=title,
            body=message,
            data=data,
            priority=priority
        )
    
    def send_daily_summary(
        self,
        push_token: str,
        total_trades: int,
        win_rate: float,
        total_pnl: float,
        active_bots: int
    ) -> Dict:
        """
        Send daily trading summary
        
        Args:
            push_token: User's push token
            total_trades: Number of trades today
            win_rate: Win rate percentage
            total_pnl: Total profit/loss
            active_bots: Number of active bots
            
        Returns:
            Notification response
        """
        pnl_emoji = "💚" if total_pnl >= 0 else "❤️"
        pnl_sign = "+" if total_pnl >= 0 else ""
        
        title = f"📊 Daily Summary"
        body = f"{pnl_emoji} P&L: {pnl_sign}${total_pnl:.2f} | Trades: {total_trades} | Win Rate: {win_rate:.1f}%"
        
        data = {
            'type': 'daily_summary',
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'active_bots': active_bots,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.send_notification(
            push_token=push_token,
            title=title,
            body=body,
            data=data,
            sound='default'
        )


# Global instance
push_service = PushNotificationService()


# Example usage
if __name__ == "__main__":
    print("\n" + "="*70)
    print("📱 Push Notification Service")
    print("="*70)
    print("\n✅ Service initialized")
    print("\n📋 Available notification types:")
    print("  - Trade notifications (buy, sell, closed)")
    print("  - Bot status updates (started, stopped, error)")
    print("  - Price alerts")
    print("  - Daily summaries")
    print("\n💡 Usage:")
    print("  from push_notifications import push_service")
    print("  push_service.send_trade_notification(token, 'buy', 'BTC/USDT', 50000, 0.1)")
    print("\n" + "="*70 + "\n")
