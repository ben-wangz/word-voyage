/**
 * Storage Interface
 * Abstract KV storage operations for Redis/TiDB compatibility
 */
export interface IStorageAdapter {
  // Basic KV operations
  get(key: string): Promise<string | null>;
  set(key: string, value: string, ttlSeconds?: number): Promise<void>;
  delete(key: string): Promise<void>;
  expire(key: string, seconds: number): Promise<void>;

  // Batch operations
  mget(keys: string[]): Promise<(string | null)[]>;

  // Set operations
  sadd(key: string, member: string): Promise<void>;
  srem(key: string, member: string): Promise<void>;
  smembers(key: string): Promise<string[]>;

  // Health check
  ping(): Promise<void>;

  // Connection management
  connect(): Promise<void>;
  disconnect(): Promise<void>;
}
