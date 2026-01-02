import { Context, Next } from 'hono';
import { getSession } from '../services/session.ts';

export function sessionRefreshMiddleware() {
  return async (c: Context, next: Next) => {
    await next();

    const sessionId = c.get('sessionId');
    if (sessionId) {
      const sessionService = getSession();
      await sessionService.refreshSession(sessionId).catch(() => {
        // Ignore errors
      });
    }
  };
}
