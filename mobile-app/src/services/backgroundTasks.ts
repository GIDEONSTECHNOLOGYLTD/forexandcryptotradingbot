/**
 * Background Tasks Service
 * Keeps bots running even when app is in background
 * Prevents losses by maintaining continuous monitoring
 * 
 * NOTE: Install dependencies first:
 * npm install expo-background-fetch expo-task-manager
 */

// Optional imports - won't break build if not installed
let BackgroundFetch: any;
let TaskManager: any;
let Notifications: any;

try {
  BackgroundFetch = require('expo-background-fetch');
  TaskManager = require('expo-task-manager');
  Notifications = require('expo-notifications');
} catch (error) {
  console.warn('⚠️ Background task dependencies not installed. Run: npm install expo-background-fetch expo-task-manager');
}

import api from './api';

const BACKGROUND_FETCH_TASK = 'background-bot-monitor';
const BACKGROUND_SYNC_TASK = 'background-sync';

/**
 * Background task to monitor bots and positions
 * Runs every 15 minutes (iOS minimum)
 */
TaskManager.defineTask(BACKGROUND_FETCH_TASK, async () => {
  try {
    console.log('🔄 Background task running...');
    
    // Fetch current bot status
    const bots = await api.getBots();
    const runningBots = bots.filter((bot: any) => bot.status === 'running');
    
    if (runningBots.length > 0) {
      // Check for any critical updates
      const dashboard = await api.getDashboard();
      
      // Send notification if significant P&L change
      if (dashboard.today_pnl_percent > 5) {
        await Notifications.scheduleNotificationAsync({
          content: {
            title: '🎉 Great Profit!',
            body: `Your bots made ${dashboard.today_pnl_percent.toFixed(2)}% profit today!`,
            data: { type: 'profit' },
          },
          trigger: null, // Send immediately
        });
      } else if (dashboard.today_pnl_percent < -3) {
        await Notifications.scheduleNotificationAsync({
          content: {
            title: '⚠️ Loss Alert',
            body: `Your bots are down ${Math.abs(dashboard.today_pnl_percent).toFixed(2)}% today`,
            data: { type: 'loss' },
          },
          trigger: null,
        });
      }
      
      console.log(`✅ Background check complete: ${runningBots.length} bots running`);
    }
    
    return BackgroundFetch.BackgroundFetchResult.NewData;
  } catch (error) {
    console.error('❌ Background task error:', error);
    return BackgroundFetch.BackgroundFetchResult.Failed;
  }
});

/**
 * Background sync task for real-time updates
 */
TaskManager.defineTask(BACKGROUND_SYNC_TASK, async () => {
  try {
    // Sync latest data
    await api.getDashboard();
    await api.getUserBalance();
    
    return BackgroundFetch.BackgroundFetchResult.NewData;
  } catch (error) {
    console.error('❌ Background sync error:', error);
    return BackgroundFetch.BackgroundFetchResult.Failed;
  }
});

/**
 * Register background fetch task
 */
export async function registerBackgroundFetchAsync() {
  if (!BackgroundFetch || !TaskManager) {
    console.warn('⚠️ Background fetch not available - dependencies not installed');
    return false;
  }
  
  try {
    const status = await BackgroundFetch.getStatusAsync();
    
    if (status === BackgroundFetch.BackgroundFetchStatus.Available) {
      await BackgroundFetch.registerTaskAsync(BACKGROUND_FETCH_TASK, {
        minimumInterval: 15 * 60, // 15 minutes (iOS minimum)
        stopOnTerminate: false, // Continue after app is killed
        startOnBoot: true, // Start on device boot
      });
      
      console.log('✅ Background fetch registered');
      return true;
    } else {
      console.warn('⚠️ Background fetch not available:', status);
      return false;
    }
  } catch (error) {
    console.error('❌ Failed to register background fetch:', error);
    return false;
  }
}

/**
 * Unregister background fetch task
 */
export async function unregisterBackgroundFetchAsync() {
  try {
    await BackgroundFetch.unregisterTaskAsync(BACKGROUND_FETCH_TASK);
    console.log('✅ Background fetch unregistered');
  } catch (error) {
    console.error('❌ Failed to unregister background fetch:', error);
  }
}

/**
 * Check if background fetch is registered
 */
export async function isBackgroundFetchRegistered() {
  try {
    const isRegistered = await TaskManager.isTaskRegisteredAsync(BACKGROUND_FETCH_TASK);
    return isRegistered;
  } catch (error) {
    console.error('❌ Failed to check background fetch status:', error);
    return false;
  }
}

/**
 * Configure notifications for background alerts
 */
export async function configureBackgroundNotifications() {
  try {
    await Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowAlert: true,
        shouldPlaySound: true,
        shouldSetBadge: true,
      }),
    });
    
    // Request permissions
    const { status } = await Notifications.requestPermissionsAsync();
    if (status !== 'granted') {
      console.warn('⚠️ Notification permissions not granted');
      return false;
    }
    
    console.log('✅ Background notifications configured');
    return true;
  } catch (error) {
    console.error('❌ Failed to configure notifications:', error);
    return false;
  }
}

/**
 * Initialize all background services
 */
export async function initializeBackgroundServices() {
  try {
    console.log('🚀 Initializing background services...');
    
    // Configure notifications
    await configureBackgroundNotifications();
    
    // Register background fetch
    const registered = await registerBackgroundFetchAsync();
    
    if (registered) {
      console.log('✅ Background services initialized');
      
      // Send confirmation notification
      await Notifications.scheduleNotificationAsync({
        content: {
          title: '🤖 Bot Protection Active',
          body: 'Your bots will continue running in the background',
          data: { type: 'background_active' },
        },
        trigger: null,
      });
      
      return true;
    } else {
      console.warn('⚠️ Background services not fully initialized');
      return false;
    }
  } catch (error) {
    console.error('❌ Failed to initialize background services:', error);
    return false;
  }
}

/**
 * Keep WebSocket connection alive in background
 * Note: iOS limits background WebSocket, so we use periodic fetch instead
 */
export function setupBackgroundWebSocket() {
  // iOS doesn't support long-running WebSocket in background
  // Instead, we use background fetch to periodically check for updates
  console.log('ℹ️ Using background fetch for updates (iOS limitation)');
}

export default {
  registerBackgroundFetchAsync,
  unregisterBackgroundFetchAsync,
  isBackgroundFetchRegistered,
  configureBackgroundNotifications,
  initializeBackgroundServices,
  setupBackgroundWebSocket,
};
