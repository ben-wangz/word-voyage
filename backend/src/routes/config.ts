import { Hono } from 'hono';
import { config } from '../config.ts';

const configRouter = new Hono();

/**
 * GET /api/config
 * Returns frontend configuration including user input limits
 */
configRouter.get('/', (c) => {
  return c.json({
    userInputLimits: config.userInputLimits,
  });
});

export default configRouter;
