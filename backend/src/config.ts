export const config = {
  port: parseInt(Bun.env.PORT || '8080', 10),
  nodeEnv: Bun.env.NODE_ENV || 'development',
  logLevel: (Bun.env.LOG_LEVEL || 'info').toLowerCase(),
  redis: {
    host: Bun.env.REDIS_HOST || 'host.containers.internal',
    port: parseInt(Bun.env.REDIS_PORT || '6379', 10),
    db: parseInt(Bun.env.REDIS_DB || '0', 10),
  },
  llm: {
    serviceUrl: Bun.env.LLM_SERVICE_URL || 'http://host.containers.internal:8011',
    timeout: parseInt(Bun.env.LLM_TIMEOUT || '30000', 10),
    contextMaxFields: parseInt(Bun.env.CONTEXT_MAX_FIELDS || '16', 10),
  },
};
