import type { IStorageAdapter } from './storage/index.ts';
import { config } from '../config.ts';

export interface User {
  userId: string;
  email?: string;
  passwordHash?: string;
  provider: 'anonymous' | 'local' | 'oidc';
  oidcSub?: string;
  createdAt: number;
  lastLoginAt: number;
}

export class UserService {
  private storage: IStorageAdapter;

  constructor(storage: IStorageAdapter) {
    this.storage = storage;
  }

  async createUser(provider: User['provider'], email?: string, oidcSub?: string): Promise<User> {
    const userId = crypto.randomUUID();
    const now = Date.now();

    const user: User = {
      userId,
      email,
      provider,
      oidcSub,
      createdAt: now,
      lastLoginAt: now,
    };

    await this.storage.set(`user:${userId}`, JSON.stringify(user), config.ttl.user);

    if (oidcSub) {
      await this.storage.set(`oidc:${oidcSub}`, userId, config.ttl.user);
    }

    return user;
  }

  async getUser(userId: string): Promise<User | null> {
    const data = await this.storage.get(`user:${userId}`);
    if (!data) return null;
    return JSON.parse(data);
  }

  async getUserByEmail(email: string): Promise<User | null> {
    const userId = await this.storage.get(`email:${email}`);
    if (!userId) return null;
    return this.getUser(userId);
  }

  async getUserByOidcSub(oidcSub: string): Promise<User | null> {
    const userId = await this.storage.get(`oidc:${oidcSub}`);
    if (!userId) return null;
    return this.getUser(userId);
  }

  async updateUser(user: User): Promise<void> {
    await this.storage.set(`user:${user.userId}`, JSON.stringify(user), config.ttl.user);
  }

  async updateLastLogin(userId: string): Promise<void> {
    const user = await this.getUser(userId);
    if (!user) {
      throw new Error(`User not found: ${userId}`);
    }

    user.lastLoginAt = Date.now();
    await this.updateUser(user);
  }

  async setUserEmail(userId: string, email: string, passwordHash: string): Promise<void> {
    const user = await this.getUser(userId);
    if (!user) {
      throw new Error(`User not found: ${userId}`);
    }

    user.email = email;
    user.passwordHash = passwordHash;
    user.provider = 'local';

    await this.updateUser(user);
    await this.storage.set(`email:${email}`, userId, config.ttl.user);
  }
}

let userInstance: UserService | null = null;

export function initUser(storage: IStorageAdapter): UserService {
  userInstance = new UserService(storage);
  return userInstance;
}

export function getUser(): UserService {
  if (!userInstance) {
    throw new Error('User service not initialized. Call initUser first.');
  }
  return userInstance;
}
