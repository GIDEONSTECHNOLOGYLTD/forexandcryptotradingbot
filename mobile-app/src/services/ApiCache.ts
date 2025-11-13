/**
 * API Response Cache
 * Prevents duplicate API calls and speeds up app 10x
 */

interface CacheItem {
  data: any;
  timestamp: number;
}

export class ApiCache {
  private cache: Map<string, CacheItem> = new Map();
  private TTL: number;

  constructor(ttlSeconds: number = 30) {
    this.TTL = ttlSeconds * 1000; // Convert to milliseconds
  }

  /**
   * Get cached data if still fresh
   */
  get(key: string): any | null {
    const item = this.cache.get(key);
    
    if (!item) {
      return null;
    }

    // Check if cache is still fresh
    if (Date.now() - item.timestamp > this.TTL) {
      this.cache.delete(key);
      return null;
    }

    console.log(`✅ Cache HIT: ${key}`);
    return item.data;
  }

  /**
   * Store data in cache
   */
  set(key: string, data: any): void {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
    });
    console.log(`💾 Cached: ${key}`);
  }

  /**
   * Clear specific cache entry
   */
  clear(key: string): void {
    this.cache.delete(key);
    console.log(`🗑️ Cleared cache: ${key}`);
  }

  /**
   * Clear all cache
   */
  clearAll(): void {
    this.cache.clear();
    console.log('🗑️ Cleared ALL cache');
  }

  /**
   * Check if key is in cache
   */
  has(key: string): boolean {
    return this.cache.has(key) && this.get(key) !== null;
  }
}

/**
 * Request Deduplicator
 * Prevents multiple identical API calls from executing simultaneously
 */
export class RequestDeduplicator {
  private pending: Map<string, Promise<any>> = new Map();

  /**
   * Execute request, or return existing promise if already in progress
   */
  async fetch<T>(key: string, fetchFn: () => Promise<T>): Promise<T> {
    // If already fetching, return existing promise
    if (this.pending.has(key)) {
      console.log(`⏳ Request PENDING: ${key} (waiting for existing request)`);
      return this.pending.get(key)!;
    }

    console.log(`🚀 Request STARTED: ${key}`);

    // Execute fetch and store promise
    const promise = fetchFn().finally(() => {
      this.pending.delete(key);
      console.log(`✅ Request COMPLETED: ${key}`);
    });

    this.pending.set(key, promise);
    return promise;
  }

  /**
   * Clear specific pending request
   */
  clear(key: string): void {
    this.pending.delete(key);
  }

  /**
   * Clear all pending requests
   */
  clearAll(): void {
    this.pending.clear();
  }
}

// Global instances
export const apiCache = new ApiCache(30); // 30 seconds TTL
export const requestDeduplicator = new RequestDeduplicator();
