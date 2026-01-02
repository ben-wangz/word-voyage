import type { IStorageAdapter } from './storage/index.ts';
import { config } from '../config.ts';

export interface SessionData {
  sessionId: string;
  userId: string;
  createdAt: number;
  lastAccessedAt: number;
  currentStepId?: string;
  stepHistory: string[];
}

export class SessionService {
  private storage: IStorageAdapter;

  constructor(storage: IStorageAdapter) {
    this.storage = storage;
  }

  async createSession(userId: string): Promise<SessionData> {
    const sessionId = crypto.randomUUID();
    const now = Date.now();

    const session: SessionData = {
      sessionId,
      userId,
      createdAt: now,
      lastAccessedAt: now,
      stepHistory: [],
    };

    await this.storage.set(`session:${sessionId}`, JSON.stringify(session), config.ttl.session);
    await this.storage.sadd(`user:${userId}:sessions`, sessionId);

    return session;
  }

  async getSession(sessionId: string): Promise<SessionData | null> {
    const data = await this.storage.get(`session:${sessionId}`);
    if (!data) return null;

    const session: SessionData = JSON.parse(data);
    session.lastAccessedAt = Date.now();

    await this.storage.set(`session:${sessionId}`, JSON.stringify(session), config.ttl.session);

    return session;
  }

  async updateCurrentStep(sessionId: string, stepId: string): Promise<void> {
    const session = await this.getSession(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }

    session.currentStepId = stepId;
    session.stepHistory.push(stepId);
    session.lastAccessedAt = Date.now();

    await this.storage.set(`session:${sessionId}`, JSON.stringify(session), config.ttl.session);
  }

  async getStepHistory(sessionId: string): Promise<string[]> {
    const session = await this.getSession(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }
    return [...session.stepHistory];
  }

  async rollbackToStep(sessionId: string, stepIndex: number): Promise<string[]> {
    const session = await this.getSession(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }

    if (stepIndex < 0 || stepIndex >= session.stepHistory.length) {
      const error: any = new Error(`Invalid step index: ${stepIndex}`);
      error.statusCode = 400;
      throw error;
    }

    const deletedStepIds = session.stepHistory.slice(stepIndex + 1);
    session.stepHistory = session.stepHistory.slice(0, stepIndex + 1);
    session.currentStepId = session.stepHistory[stepIndex];
    session.lastAccessedAt = Date.now();

    await this.storage.set(`session:${sessionId}`, JSON.stringify(session), config.ttl.session);
    return deletedStepIds;
  }

  async deleteSession(sessionId: string): Promise<void> {
    const session = await this.getSession(sessionId);
    if (session) {
      await this.storage.srem(`user:${session.userId}:sessions`, sessionId);
    }
    await this.storage.delete(`session:${sessionId}`);
  }

  async getUserSessions(userId: string): Promise<string[]> {
    return await this.storage.smembers(`user:${userId}:sessions`);
  }

  async refreshSession(sessionId: string): Promise<void> {
    await this.storage.expire(`session:${sessionId}`, config.ttl.session);
  }
}

let sessionInstance: SessionService | null = null;

export function initSession(storage: IStorageAdapter): SessionService {
  sessionInstance = new SessionService(storage);
  return sessionInstance;
}

export function getSession(): SessionService {
  if (!sessionInstance) {
    throw new Error('Session service not initialized. Call initSession first.');
  }
  return sessionInstance;
}
