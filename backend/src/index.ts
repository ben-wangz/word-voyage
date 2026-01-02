import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { config } from './config.ts';
import { RedisAdapter } from './services/storage/index.ts';
import { initSession } from './services/session.ts';
import { initStepStorage } from './services/stepStorage.ts';
import { initUser } from './services/user.ts';
import { initAuth } from './services/auth.ts';
import { initializeI18n } from './i18n/index.ts';
import { i18nMiddleware } from './i18n/middleware.ts';
import { cookieMiddleware } from './middleware/cookie.ts';
import { authMiddleware } from './middleware/auth.ts';
import { sessionRefreshMiddleware } from './middleware/sessionRefresh.ts';
import gameRouter from './routes/game.ts';
import authRouter from './routes/auth.ts';
import healthRouter from './routes/health.ts';

const app = new Hono();

// Middleware
app.use('*', logger());
app.use('*', cors({ credentials: true }));
app.use('*', i18nMiddleware());
app.use('*', cookieMiddleware());
app.use('*', authMiddleware());
app.use('*', sessionRefreshMiddleware());

// Routes
app.route('/api/auth', authRouter);
app.route('/api/game', gameRouter);
app.route('/api/health', healthRouter);

// Root endpoint
app.get('/', (c) => {
  return c.json({
    name: 'WordVoyage Backend API',
    version: '1.0.0',
    endpoints: {
      auth: '/api/auth',
      game: '/api/game',
      health: '/api/health',
    },
  });
});

async function initialize() {
  console.log('Initializing backend services...');

  try {
    await initializeI18n();
    console.log(`i18n initialized (default language: ${config.defaultLanguage})`);

    const storage = new RedisAdapter(config.redis);
    await storage.connect();
    console.log('Redis storage connected');

    initSession(storage);
    console.log('Session service initialized');

    initStepStorage(storage);
    console.log('Step storage service initialized');

    initUser(storage);
    console.log('User service initialized');

    initAuth(storage, config.jwt);
    console.log('Auth service initialized');

    console.log('Backend services initialized successfully');
  } catch (error) {
    console.error('Failed to initialize services:', error);
    process.exit(1);
  }
}

async function main() {
  await initialize();

  console.log(`Server starting on port ${config.port}...`);

  Bun.serve({
    fetch: app.fetch,
    port: config.port,
  });

  console.log(`Server running at http://localhost:${config.port}`);
}

main();
