/**
 * Push Notification Service for iOS
 * Handles registration, permissions, and receiving notifications
 */
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import * as api from './api';

// Configure how notifications should be handled when app is in foreground
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

export class NotificationService {
  private static pushToken: string | null = null;

  /**
   * Request notification permissions and get push token
   */
  static async registerForPushNotifications(): Promise<string | null> {
    try {
      // Check if running on real device
      if (!Device.isDevice) {
        console.log('⚠️ Push notifications only work on physical devices');
        return null;
      }

      // Request permissions
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;

      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }

      if (finalStatus !== 'granted') {
        console.log('⚠️ Notification permissions not granted');
        return null;
      }

      // Get push token
      const token = (await Notifications.getExpoPushTokenAsync()).data;
      console.log('✅ Push token:', token);

      // Save token to backend
      try {
        await api.savePushToken(token);
        console.log('✅ Push token saved to backend');
      } catch (error) {
        console.error('❌ Failed to save push token:', error);
      }

      this.pushToken = token;
      return token;
    } catch (error) {
      console.error('❌ Error registering for push notifications:', error);
      return null;
    }
  }

  /**
   * Set up notification listeners
   */
  static setupNotificationListeners(
    onNotificationReceived?: (notification: Notifications.Notification) => void,
    onNotificationResponse?: (response: Notifications.NotificationResponse) => void
  ) {
    // Listener for notifications received while app is foregrounded
    const foregroundSubscription = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('📱 Notification received:', notification);
        if (onNotificationReceived) {
          onNotificationReceived(notification);
        }
      }
    );

    // Listener for when user taps on notification
    const responseSubscription = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('👆 Notification tapped:', response);
        if (onNotificationResponse) {
          onNotificationResponse(response);
        }
      }
    );

    return {
      foregroundSubscription,
      responseSubscription,
    };
  }

  /**
   * Send a local notification (for testing)
   */
  static async sendLocalNotification(title: string, body: string, data?: any) {
    try {
      await Notifications.scheduleNotificationAsync({
        content: {
          title,
          body,
          data,
          sound: true,
        },
        trigger: null, // Send immediately
      });
      console.log('✅ Local notification sent');
    } catch (error) {
      console.error('❌ Error sending local notification:', error);
    }
  }

  /**
   * Get current badge count
   */
  static async getBadgeCount(): Promise<number> {
    try {
      return await Notifications.getBadgeCountAsync();
    } catch (error) {
      console.error('❌ Error getting badge count:', error);
      return 0;
    }
  }

  /**
   * Set badge count
   */
  static async setBadgeCount(count: number) {
    try {
      await Notifications.setBadgeCountAsync(count);
      console.log(`✅ Badge count set to ${count}`);
    } catch (error) {
      console.error('❌ Error setting badge count:', error);
    }
  }

  /**
   * Clear all notifications
   */
  static async clearAllNotifications() {
    try {
      await Notifications.dismissAllNotificationsAsync();
      await this.setBadgeCount(0);
      console.log('✅ All notifications cleared');
    } catch (error) {
      console.error('❌ Error clearing notifications:', error);
    }
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
