import { Context, Next } from 'hono';
import { getCookie, setCookie } from 'hono/cookie';
import { getSession } from '../services/session.ts';
import { getUser } from '../services/user.ts';
import { config } from '../config.ts';

export function cookieMiddleware() {
  return async (c: Context, next: Next) => {
    const sessionService = getSession();
    const userService = getUser();

    let sessionId = getCookie(c, config.session.cookieName);
    let userId: string;

    if (sessionId) {
      const session = await sessionService.getSession(sessionId);
      if (session) {
        userId = session.userId;
        c.set('sessionId', sessionId);
        c.set('userId', userId);
        await next();
        return;
      }
    }

    const user = await userService.createUser('anonymous');
    const session = await sessionService.createSession(user.userId);

    setCookie(c, config.session.cookieName, session.sessionId, {
      httpOnly: true,
      sameSite: 'Lax',
      maxAge: config.ttl.cookie,
      path: '/',
    });

    c.set('sessionId', session.sessionId);
    c.set('userId', user.userId);

    await next();
  };
}
