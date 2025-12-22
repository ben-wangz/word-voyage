import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';
import { config } from './config.ts';
import { initSession } from './services/session.ts';
import { initStepStorage } from './services/stepStorage.ts';
import { initRedis } from './services/redis.ts';
import gameRouter from './routes/game.ts';
import healthRouter from './routes/health.ts';

const app = new Hono();

// Middleware
app.use('*', logger());
app.use('*', cors());

// Routes
app.route('/api/game', gameRouter);
app.route('/api/health', healthRouter);

// Root endpoint
app.get('/', (c) => {
  return c.json({
    name: 'WordVoyage Backend API',
    version: '1.0.0',
    endpoints: {
      game: '/api/game',
      health: '/api/health',
    },
  });
});

// Initialize services on startup
async function initialize() {
  console.log('Initializing backend services...');

  try {
    // Initialize session service
    initSession();
    console.log('Session service initialized');

    // Initialize step storage
    initStepStorage();
    console.log('Step storage service initialized');

    // Initialize Redis (MVP: skipped, will use in phase 2)
    // const redis = initRedis(config.redis);
    // await redis.connect();
    // console.log('Redis service initialized');

    console.log('Backend services initialized successfully');
  } catch (error) {
    console.error('Failed to initialize services:', error);
    process.exit(1);
  }
}

// Start server
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
