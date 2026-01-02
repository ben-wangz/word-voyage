import { Hono } from 'hono';
import { getAuth } from '../services/auth.ts';
import { getUser } from '../services/user.ts';
import { getSession } from '../services/session.ts';
import type { I18nContext } from '../types/index.ts';

const authRouter = new Hono();

interface RegisterRequest {
  email: string;
  password: string;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RefreshRequest {
  refreshToken: string;
}

authRouter.post('/register', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const body = await c.req.json<RegisterRequest>();
    const { email, password } = body;

    if (!email || !password) {
      return c.json({ error: { code: 'INVALID_INPUT', message: t('common:errors.emailPasswordRequired', 'Email and password required') } }, 400);
    }

    const authService = getAuth();
    const userService = getUser();

    const existingUser = await userService.getUserByEmail(email);
    if (existingUser) {
      return c.json({ error: { code: 'EMAIL_EXISTS', message: t('auth:errors.emailExists', 'Email already registered') } }, 400);
    }

    const userId = c.get('userId') as string;
    const passwordHash = await authService.hashPassword(password);

    await userService.setUserEmail(userId, email, passwordHash);

    const tokens = await authService.generateTokens(userId);

    return c.json({
      user: { userId, email },
      ...tokens,
    });
  } catch (error: any) {
    console.error('Error registering user:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

authRouter.post('/login', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const body = await c.req.json<LoginRequest>();
    const { email, password } = body;

    if (!email || !password) {
      return c.json({ error: { code: 'INVALID_INPUT', message: t('common:errors.emailPasswordRequired', 'Email and password required') } }, 400);
    }

    const authService = getAuth();
    const userService = getUser();

    const user = await userService.getUserByEmail(email);
    if (!user || !user.passwordHash) {
      return c.json({ error: { code: 'INVALID_CREDENTIALS', message: t('auth:errors.invalidCredentials', 'Invalid email or password') } }, 401);
    }

    const valid = await authService.verifyPassword(password, user.passwordHash);
    if (!valid) {
      return c.json({ error: { code: 'INVALID_CREDENTIALS', message: t('auth:errors.invalidCredentials', 'Invalid email or password') } }, 401);
    }

    await userService.updateLastLogin(user.userId);

    const tokens = await authService.generateTokens(user.userId);

    return c.json({
      user: { userId: user.userId, email: user.email },
      ...tokens,
    });
  } catch (error: any) {
    console.error('Error logging in:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

authRouter.post('/refresh', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const body = await c.req.json<RefreshRequest>();
    const { refreshToken } = body;

    if (!refreshToken) {
      return c.json({ error: { code: 'INVALID_INPUT', message: t('auth:errors.refreshTokenRequired', 'Refresh token required') } }, 400);
    }

    const authService = getAuth();
    const tokens = await authService.refreshAccessToken(refreshToken);

    return c.json(tokens);
  } catch (error: any) {
    console.error('Error refreshing token:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INVALID_TOKEN', message: t('auth:errors.invalidRefreshToken', 'Invalid or expired refresh token') } }, 401);
  }
});

authRouter.post('/logout', async (c) => {
  try {
    const t = c.get('t') as I18nContext['t'];
    const body = await c.req.json<RefreshRequest>();
    const { refreshToken } = body;

    if (refreshToken) {
      const authService = getAuth();
      await authService.revokeRefreshToken(refreshToken);
    }

    const sessionId = c.get('sessionId') as string;
    if (sessionId) {
      const sessionService = getSession();
      await sessionService.deleteSession(sessionId);
    }

    return c.json({ message: t('auth:success.loggedOut', 'Logged out successfully') });
  } catch (error: any) {
    console.error('Error logging out:', error);
    const t = c.get('t') as I18nContext['t'];
    return c.json({ error: { code: 'INTERNAL_ERROR', message: t('common:errors.internalError', error.message) } }, 500);
  }
});

authRouter.get('/oidc/authorize', async (c) => {
  return c.json({ error: { code: 'NOT_IMPLEMENTED', message: 'OIDC not implemented' } }, 501);
});

authRouter.get('/oidc/callback', async (c) => {
  return c.json({ error: { code: 'NOT_IMPLEMENTED', message: 'OIDC not implemented' } }, 501);
});

export default authRouter;
