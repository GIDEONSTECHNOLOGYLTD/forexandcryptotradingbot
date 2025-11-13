/**
 * Push Notification Service for iOS
 * STUB VERSION - Install expo-notifications and expo-device to activate
 * 
 * To enable: npx expo install expo-notifications expo-device
 */

/**
 * Notification Service (Stub)
 * Currently using Telegram for notifications
 * iOS push notifications ready to activate when needed
 */
export class NotificationService {
  private static pushToken: string | null = null;

  /**
   * Request notification permissions and get push token
   * TODO: Implement when expo-notifications is installed
   */
  static async registerForPushNotifications(): Promise<string | null> {
    console.log('📱 Push notifications not enabled yet');
    console.log('💡 Install: npx expo install expo-notifications expo-device');
    return null;
  }

  /**
   * Set up notification listeners
   * TODO: Implement when expo-notifications is installed
   */
  static setupNotificationListeners(
    onNotificationReceived?: (notification: any) => void,
    onNotificationResponse?: (response: any) => void
  ) {
    console.log('📱 Notification listeners not enabled yet');
    return {
      foregroundSubscription: { remove: () => {} },
      responseSubscription: { remove: () => {} },
    };
  }

  /**
   * Send a local notification (for testing)
   * TODO: Implement when expo-notifications is installed
   */
  static async sendLocalNotification(title: string, body: string, data?: any) {
    console.log(`📱 Local notification: ${title} - ${body}`);
  }

  /**
   * Get current badge count
   */
  static async getBadgeCount(): Promise<number> {
    return 0;
  }

  /**
   * Set badge count
   */
  static async setBadgeCount(count: number) {
    console.log(`📱 Badge count: ${count}`);
  }

  /**
   * Clear all notifications
   */
  static async clearAllNotifications() {
    console.log('📱 Notifications cleared');
  }

  /**
   * Get push token (if already registered)
   */
  static getPushToken(): string | null {
    return this.pushToken;
  }
}

/**
 * Notification types that can be received
 */
export enum NotificationType {
  TRADE_EXECUTED = 'trade_executed',
  BOT_STARTED = 'bot_started',
  BOT_STOPPED = 'bot_stopped',
  PROFIT_ALERT = 'profit_alert',
  LOSS_ALERT = 'loss_alert',
  PRICE_ALERT = 'price_alert',
  SYSTEM_ALERT = 'system_alert',
}

/**
 * Notification data structure
 */
export interface NotificationData {
  type: NotificationType;
  botId?: string;
  symbol?: string;
  price?: number;
  pnl?: number;
  message?: string;
}

// Export for compatibility
export default NotificationService;
