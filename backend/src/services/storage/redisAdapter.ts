import Redis from 'ioredis';
import type { IStorageAdapter } from './interface.ts';

export interface RedisConfig {
  host: string;
  port: number;
  db?: number;
  password?: string;
}

export class RedisAdapter implements IStorageAdapter {
  private client: Redis;

  constructor(config: RedisConfig) {
    this.client = new Redis({
      host: config.host,
      port: config.port,
      db: config.db || 0,
      password: config.password,
      maxRetriesPerRequest: 3,
      enableReadyCheck: true,
      lazyConnect: true,
    });
  }

  async connect(): Promise<void> {
    await this.client.connect();
  }

  async disconnect(): Promise<void> {
    await this.client.quit();
  }

  async ping(): Promise<void> {
    await this.client.ping();
  }

  async get(key: string): Promise<string | null> {
    return await this.client.get(key);
  }

  async set(key: string, value: string, ttlSeconds?: number): Promise<void> {
    if (ttlSeconds) {
      await this.client.setex(key, ttlSeconds, value);
    } else {
      await this.client.set(key, value);
    }
  }

  async delete(key: string): Promise<void> {
    await this.client.del(key);
  }

  async expire(key: string, seconds: number): Promise<void> {
    await this.client.expire(key, seconds);
  }

  async mget(keys: string[]): Promise<(string | null)[]> {
    if (keys.length === 0) return [];
    return await this.client.mget(...keys);
  }

  async sadd(key: string, member: string): Promise<void> {
    await this.client.sadd(key, member);
  }

  async srem(key: string, member: string): Promise<void> {
    await this.client.srem(key, member);
  }

  async smembers(key: string): Promise<string[]> {
    return await this.client.smembers(key);
  }
}
