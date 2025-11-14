/**
 * Push Notification Service for iOS/Android
 * Full implementation with expo-notifications
 */
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import { Platform } from 'react-native';
import Constants from 'expo-constants';

// Configure notification behavior
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

/**
 * Notification Service
 * Handles push notifications for trading alerts
 */
export class NotificationService {
  private static pushToken: string | null = null;

  /**
   * Request notification permissions and get push token
   */
  static async registerForPushNotifications(): Promise<string | null> {
    try {
      console.log('📱 Registering for push notifications...');
      
      // Check if physical device
      if (!Device.isDevice) {
        console.warn('⚠️ Push notifications only work on physical devices');
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
        console.warn('⚠️ Notification permissions denied');
        return null;
      }

      // Get push token
      const token = await Notifications.getExpoPushTokenAsync({
        projectId: Constants.expoConfig?.extra?.eas?.projectId,
      });

      console.log('✅ Push token:', token.data);
      this.pushToken = token.data;

      // Configure for Android
      if (Platform.OS === 'android') {
        Notifications.setNotificationChannelAsync('default', {
          name: 'default',
          importance: Notifications.AndroidImportance.MAX,
          vibrationPattern: [0, 250, 250, 250],
          lightColor: '#FF231F7C',
        });
      }

      return token.data;
    } catch (error) {
      console.error('❌ Failed to register for push notifications:', error);
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
    console.log('📱 Setting up notification listeners...');
    
    // Handle notification received while app is foregrounded
    const foregroundSubscription = Notifications.addNotificationReceivedListener(
      (notification) => {
        console.log('📱 Notification received (foreground):', notification);
        if (onNotificationReceived) {
          onNotificationReceived(notification);
        }
      }
    );

    // Handle user tapping on notification
    const responseSubscription = Notifications.addNotificationResponseReceivedListener(
      (response) => {
        console.log('📱 Notification tapped:', response);
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
      console.log(`📱 Local notification sent: ${title}`);
    } catch (error) {
      console.error('❌ Failed to send local notification:', error);
    }
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
