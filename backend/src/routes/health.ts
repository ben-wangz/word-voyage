import { Hono } from 'hono';

const healthRouter = new Hono();

healthRouter.get('/', (c) => {
  return c.json({
    status: 'ok',
    service: 'WordVoyage Backend API',
    timestamp: new Date().toISOString(),
  });
});

export default healthRouter;
