import { Step } from '../types/index.ts';

/**
 * Session Management Service
 * Manage user sessions and current game state
 */
export interface SessionData {
  sessionId: string;
  createdAt: number;
  lastAccessedAt: number;
  currentStepId?: string;
  stepHistory: string[]; // Step IDs
}

export class SessionService {
  private sessions: Map<string, SessionData> = new Map();

  /**
 * Create new session
 */
  createSession(): SessionData {
    const sessionId = crypto.randomUUID();
    const now = Date.now();

    const session: SessionData = {
      sessionId,
      createdAt: now,
      lastAccessedAt: now,
      stepHistory: [],
    };

    this.sessions.set(sessionId, session);
    return session;
  }

  /**
 * Get session
 */
  getSession(sessionId: string): SessionData | null {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.lastAccessedAt = Date.now();
    }
    return session || null;
  }

  /**
 * Update current step
 */
  updateCurrentStep(sessionId: string, stepId: string): void {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }

    session.currentStepId = stepId;
    session.stepHistory.push(stepId);
    session.lastAccessedAt = Date.now();
  }

  /**
 * Get step history
 */
  getStepHistory(sessionId: string): string[] {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session not found: ${sessionId}`);
    }
    return [...session.stepHistory];
  }

  /**
 * Delete session
 */
  deleteSession(sessionId: string): void {
    this.sessions.delete(sessionId);
  }

  /**
 * Clean up expired sessions (7 days)
 */
  cleanupExpiredSessions(): void {
    const now = Date.now();
    const maxAge = 7 * 24 * 60 * 60 * 1000;

    for (const [sessionId, session] of this.sessions.entries()) {
      if (now - session.lastAccessedAt > maxAge) {
        this.sessions.delete(sessionId);
      }
    }
  }
}

// Global singleton
let sessionInstance: SessionService | null = null;

export function initSession(): SessionService {
  sessionInstance = new SessionService();
  return sessionInstance;
}

export function getSession(): SessionService {
  if (!sessionInstance) {
    throw new Error('Session service not initialized. Call initSession first.');
  }
  return sessionInstance;
}
