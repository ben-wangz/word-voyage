import { Context, Next } from 'hono';
import { getAuth } from '../services/auth.ts';

export function authMiddleware(options: { required?: boolean } = {}) {
  return async (c: Context, next: Next) => {
    const authService = getAuth();
    const authHeader = c.req.header('Authorization');

    if (!authHeader) {
      if (options.required) {
        return c.json({ error: { code: 'UNAUTHORIZED', message: 'Authorization required' } }, 401);
      }
      await next();
      return;
    }

    const [type, token] = authHeader.split(' ');
    if (type !== 'Bearer' || !token) {
      if (options.required) {
        return c.json({ error: { code: 'INVALID_TOKEN', message: 'Invalid authorization format' } }, 401);
      }
      await next();
      return;
    }

    try {
      const { userId } = authService.verifyAccessToken(token);
      c.set('userId', userId);
      c.set('authenticated', true);
      await next();
    } catch (error) {
      if (options.required) {
        return c.json({ error: { code: 'INVALID_TOKEN', message: 'Invalid or expired token' } }, 401);
      }
      await next();
    }
  };
}
