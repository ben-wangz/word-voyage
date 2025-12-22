/**
 * Redis KV Storage Service
 * MVP phase simplified implementation
 */

interface RedisConfig {
  host: string;
  port: number;
  db?: number;
}

export class RedisService {
  private config: RedisConfig;
  private connected: boolean = false;

  constructor(config: RedisConfig) {
    this.config = config;
  }

  /**
 * Connect to Redis
 */
  async connect(): Promise<void> {
    try {
      // MVP phase: use Bun built-in Redis or third-party library
      // Specific implementation in phase 2
      console.log(`Connecting to Redis at ${this.config.host}:${this.config.port}`);
      this.connected = true;
    } catch (error) {
      throw new Error(`Failed to connect to Redis: ${error}`);
    }
  }

  /**
 * Disconnect
 */
  async disconnect(): Promise<void> {
    this.connected = false;
  }

  /**
 * Set value
 */
  async set(key: string, value: unknown, ttl?: number): Promise<void> {
    if (!this.connected) {
      throw new Error('Redis not connected');
    }
    // Implementation in phase 2
    console.log(`Redis SET: ${key}`);
  }

  /**
 * Get value
 */
  async get<T>(key: string): Promise<T | null> {
    if (!this.connected) {
      throw new Error('Redis not connected');
    }
    // Implementation in phase 2
    console.log(`Redis GET: ${key}`);
    return null;
  }

  /**
 * Delete value
 */
  async delete(key: string): Promise<void> {
    if (!this.connected) {
      throw new Error('Redis not connected');
    }
    // Implementation in phase 2
    console.log(`Redis DELETE: ${key}`);
  }

  /**
 * Check if connected
 */
  isConnected(): boolean {
    return this.connected;
  }
}

// Global singleton
let redisInstance: RedisService | null = null;

export function initRedis(config: RedisConfig): RedisService {
  redisInstance = new RedisService(config);
  return redisInstance;
}

export function getRedis(): RedisService {
  if (!redisInstance) {
    throw new Error('Redis not initialized. Call initRedis first.');
  }
  return redisInstance;
}
