export const config = {
  port: parseInt(Bun.env.PORT || '8080', 10),
  nodeEnv: Bun.env.NODE_ENV || 'development',
  redis: {
    host: Bun.env.REDIS_HOST || 'localhost',
    port: parseInt(Bun.env.REDIS_PORT || '6379', 10),
    db: parseInt(Bun.env.REDIS_DB || '0', 10),
  },
};
