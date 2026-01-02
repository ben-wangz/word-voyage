import jwt from 'jsonwebtoken';
import type { IStorageAdapter } from './storage/index.ts';
import { config } from '../config.ts';

export interface JWTConfig {
  secret: string;
  accessTokenExpiry: string;
  refreshTokenExpiry: string;
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
}

interface RefreshTokenData {
  tokenId: string;
  userId: string;
  createdAt: number;
  expiresAt: number;
}

export class AuthService {
  private storage: IStorageAdapter;
  private jwtConfig: JWTConfig;

  constructor(storage: IStorageAdapter, jwtConfig: JWTConfig) {
    this.storage = storage;
    this.jwtConfig = jwtConfig;
  }

  async generateTokens(userId: string): Promise<TokenPair> {
    const accessToken = jwt.sign({ userId }, this.jwtConfig.secret, {
      expiresIn: this.jwtConfig.accessTokenExpiry,
    });

    const tokenId = crypto.randomUUID();
    const now = Date.now();
    const expiresAt = now + config.ttl.refreshToken * 1000;

    const refreshTokenData: RefreshTokenData = {
      tokenId,
      userId,
      createdAt: now,
      expiresAt,
    };

    await this.storage.set(`refresh:${tokenId}`, JSON.stringify(refreshTokenData), config.ttl.refreshToken);

    const refreshToken = jwt.sign({ tokenId, userId }, this.jwtConfig.secret, {
      expiresIn: this.jwtConfig.refreshTokenExpiry,
    });

    return { accessToken, refreshToken };
  }

  verifyAccessToken(token: string): { userId: string } {
    try {
      const payload = jwt.verify(token, this.jwtConfig.secret) as { userId: string };
      return { userId: payload.userId };
    } catch (error) {
      throw new Error('Invalid access token');
    }
  }

  async verifyRefreshToken(token: string): Promise<{ userId: string }> {
    try {
      const payload = jwt.verify(token, this.jwtConfig.secret) as { tokenId: string; userId: string };

      const data = await this.storage.get(`refresh:${payload.tokenId}`);
      if (!data) {
        throw new Error('Refresh token revoked or expired');
      }

      const tokenData: RefreshTokenData = JSON.parse(data);

      if (tokenData.expiresAt < Date.now()) {
        await this.storage.delete(`refresh:${payload.tokenId}`);
        throw new Error('Refresh token expired');
      }

      return { userId: tokenData.userId };
    } catch (error) {
      throw new Error('Invalid refresh token');
    }
  }

  async refreshAccessToken(refreshToken: string): Promise<TokenPair> {
    const { userId } = await this.verifyRefreshToken(refreshToken);
    return this.generateTokens(userId);
  }

  async revokeRefreshToken(token: string): Promise<void> {
    try {
      const payload = jwt.verify(token, this.jwtConfig.secret) as { tokenId: string };
      await this.storage.delete(`refresh:${payload.tokenId}`);
    } catch (error) {
      console.error('Failed to revoke refresh token:', error);
    }
  }

  async hashPassword(password: string): Promise<string> {
    const hasher = new Bun.CryptoHasher('sha256');
    hasher.update(password);
    return hasher.digest('hex');
  }

  async verifyPassword(password: string, hash: string): Promise<boolean> {
    const computed = await this.hashPassword(password);
    return computed === hash;
  }
}

let authInstance: AuthService | null = null;

export function initAuth(storage: IStorageAdapter, config: JWTConfig): AuthService {
  authInstance = new AuthService(storage, config);
  return authInstance;
}

export function getAuth(): AuthService {
  if (!authInstance) {
    throw new Error('Auth service not initialized. Call initAuth first.');
  }
  return authInstance;
}
