/**
 * Offline Mode Service
 * Handles data caching and offline functionality
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';

interface CachedData {
  data: any;
  timestamp: number;
  expiresIn: number; // milliseconds
}

const CACHE_PREFIX = 'cache_';
const OFFLINE_QUEUE_KEY = 'offline_queue';

export class OfflineService {
  private static isOnline: boolean = true;
  private static listeners: Array<(isOnline: boolean) => void> = [];

  /**
   * Initialize offline service
   */
  static async init() {
    // Subscribe to network state
    NetInfo.addEventListener((state) => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected ?? false;

      // Notify listeners
      if (wasOnline !== this.isOnline) {
        this.listeners.forEach((listener) => listener(this.isOnline));
        
        // Process offline queue when coming online
        if (this.isOnline) {
          this.processOfflineQueue();
        }
      }
    });
  }

  /**
   * Check if device is online
   */
  static isDeviceOnline(): boolean {
    return this.isOnline;
  }

  /**
   * Add network status listener
   */
  static addListener(listener: (isOnline: boolean) => void) {
    this.listeners.push(listener);
  }

  /**
   * Remove network status listener
   */
  static removeListener(listener: (isOnline: boolean) => void) {
    this.listeners = this.listeners.filter((l) => l !== listener);
  }

  /**
   * Cache data
   */
  static async cacheData(key: string, data: any, expiresIn: number = 3600000) {
    try {
      const cachedData: CachedData = {
        data,
        timestamp: Date.now(),
        expiresIn,
      };
      
      await AsyncStorage.setItem(
        `${CACHE_PREFIX}${key}`,
        JSON.stringify(cachedData)
      );
    } catch (error) {
      console.error('Error caching data:', error);
    }
  }

  /**
   * Get cached data
   */
  static async getCachedData(key: string): Promise<any | null> {
    try {
      const cached = await AsyncStorage.getItem(`${CACHE_PREFIX}${key}`);
      
      if (!cached) {
        return null;
      }

      const cachedData: CachedData = JSON.parse(cached);
      
      // Check if expired
      if (Date.now() - cachedData.timestamp > cachedData.expiresIn) {
        await this.clearCache(key);
        return null;
      }

      return cachedData.data;
    } catch (error) {
      console.error('Error getting cached data:', error);
      return null;
    }
  }

  /**
   * Clear specific cache
   */
  static async clearCache(key: string) {
    try {
      await AsyncStorage.removeItem(`${CACHE_PREFIX}${key}`);
    } catch (error) {
      console.error('Error clearing cache:', error);
    }
  }

  /**
   * Clear all cache
   */
  static async clearAllCache() {
    try {
      const keys = await AsyncStorage.getAllKeys();
      const cacheKeys = keys.filter((key) => key.startsWith(CACHE_PREFIX));
      await AsyncStorage.multiRemove(cacheKeys);
    } catch (error) {
      console.error('Error clearing all cache:', error);
    }
  }

  /**
   * Queue action for when device comes online
   */
  static async queueAction(action: {
    type: string;
    endpoint: string;
    method: string;
    data?: any;
  }) {
    try {
      const queue = await this.getOfflineQueue();
      queue.push({
        ...action,
        timestamp: Date.now(),
      });
      
      await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
    } catch (error) {
      console.error('Error queuing action:', error);
    }
  }

  /**
   * Get offline queue
   */
  static async getOfflineQueue(): Promise<any[]> {
    try {
      const queue = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
      return queue ? JSON.parse(queue) : [];
    } catch (error) {
      console.error('Error getting offline queue:', error);
      return [];
    }
  }

  /**
   * Process offline queue
   */
  static async processOfflineQueue() {
    try {
      const queue = await this.getOfflineQueue();
      
      if (queue.length === 0) {
        return;
      }

      console.log(`Processing ${queue.length} queued actions...`);

      // Process each action
      for (const action of queue) {
        try {
          // TODO: Execute the queued action
          // This would call your API service
          console.log('Processing action:', action.type);
        } catch (error) {
          console.error('Error processing action:', error);
        }
      }

      // Clear queue after processing
      await AsyncStorage.removeItem(OFFLINE_QUEUE_KEY);
    } catch (error) {
      console.error('Error processing offline queue:', error);
    }
  }

  /**
   * Get cached or fetch data
   */
  static async getCachedOrFetch<T>(
    key: string,
    fetchFn: () => Promise<T>,
    expiresIn: number = 3600000
  ): Promise<T> {
    // Try cache first
    const cached = await this.getCachedData(key);
    
    if (cached) {
      return cached as T;
    }

    // If offline, return null or throw
    if (!this.isOnline) {
      throw new Error('No cached data available and device is offline');
    }

    // Fetch fresh data
    const data = await fetchFn();
    
    // Cache it
    await this.cacheData(key, data, expiresIn);
    
    return data;
  }
}

// Initialize on import
OfflineService.init();
