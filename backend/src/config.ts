const parseTTL = (value: string | undefined, defaultSeconds: number): number => {
  if (!value) return defaultSeconds;
  const num = parseInt(value, 10);
  return isNaN(num) ? defaultSeconds : num;
};

const rawConfig = {
  port: parseInt(Bun.env.PORT || '8080', 10),
  nodeEnv: Bun.env.NODE_ENV || 'development',
  logLevel: (Bun.env.LOG_LEVEL || 'info').toLowerCase(),
  defaultLanguage: (Bun.env.DEFAULT_LANGUAGE || 'en') as 'en' | 'zh',
  redis: {
    host: Bun.env.REDIS_HOST || 'host.containers.internal',
    port: parseInt(Bun.env.REDIS_PORT || '6379', 10),
    db: parseInt(Bun.env.REDIS_DB || '0', 10),
    password: Bun.env.REDIS_PASSWORD,
  },
  ttl: {
    session: parseTTL(Bun.env.TTL_SESSION, 7 * 24 * 60 * 60),
    step: parseTTL(Bun.env.TTL_STEP, 30 * 24 * 60 * 60),
    user: parseTTL(Bun.env.TTL_USER, 365 * 24 * 60 * 60),
    refreshToken: parseTTL(Bun.env.TTL_REFRESH_TOKEN, 7 * 24 * 60 * 60),
    cookie: parseTTL(Bun.env.TTL_COOKIE, 7 * 24 * 60 * 60),
  },
  session: {
    cookieName: Bun.env.SESSION_COOKIE_NAME || 'sid',
  },
  jwt: {
    secret: Bun.env.JWT_SECRET || 'change-this-secret-in-production',
    accessTokenExpiry: Bun.env.JWT_ACCESS_EXPIRY || '15m',
    refreshTokenExpiry: Bun.env.JWT_REFRESH_EXPIRY || '7d',
  },
  llm: {
    serviceUrl: Bun.env.LLM_SERVICE_URL || 'http://host.containers.internal:8011',
    timeout: parseInt(Bun.env.LLM_TIMEOUT || '60000', 10),
    maxTokens: parseInt(Bun.env.LLM_MAX_TOKENS || '3000', 10),
    contextMaxFields: parseInt(Bun.env.CONTEXT_MAX_FIELDS || '16', 10),
    userInputTokensLimit: parseInt(Bun.env.USER_INPUT_TOKENS_LIMIT || '300', 10),
    eventDescriptionTokensLimit: parseInt(Bun.env.EVENT_DESCRIPTION_TOKENS_LIMIT || '500', 10),
  },
  openai: {
    baseUrl: Bun.env.OPENAI_BASE_URL || 'https://api.openai.com/v1',
    apiKey: Bun.env.OPENAI_API_KEY || '',
    model: Bun.env.OPENAI_API_MODEL || 'gpt-4o',
  },
};

function validateTTL(config: typeof rawConfig): void {
  const { session, step, user, refreshToken, cookie } = config.ttl;

  if (step < session) {
    throw new Error('TTL_STEP must be >= TTL_SESSION (steps should outlive sessions)');
  }

  if (session !== cookie) {
    throw new Error('TTL_SESSION must equal TTL_COOKIE (session and cookie must expire together)');
  }

  if (refreshToken !== session) {
    throw new Error('TTL_REFRESH_TOKEN must equal TTL_SESSION (refresh token should match session lifetime)');
  }

  if (user < session) {
    throw new Error('TTL_USER must be >= TTL_SESSION (users should outlive sessions)');
  }
}

validateTTL(rawConfig);

// Calculate derived limits for user input and event description
const userInputLimits = {
  zh: {
    chars: Math.floor(rawConfig.llm.userInputTokensLimit / 2), // tokens ÷ 2 for Chinese
  },
  en: {
    chars: rawConfig.llm.userInputTokensLimit * 4, // tokens × 4 for English
  },
};

const eventDescriptionGuidance = {
  zh: {
    tokens: rawConfig.llm.eventDescriptionTokensLimit,
    chars: Math.floor(rawConfig.llm.eventDescriptionTokensLimit / 2),
    description: `生成约 ${rawConfig.llm.eventDescriptionTokensLimit} tokens 的事件描述（约 ${Math.floor(rawConfig.llm.eventDescriptionTokensLimit / 2)} 个汉字）`,
  },
  en: {
    tokens: rawConfig.llm.eventDescriptionTokensLimit,
    chars: rawConfig.llm.eventDescriptionTokensLimit * 4,
    description: `Generate event_description with approximately ${rawConfig.llm.eventDescriptionTokensLimit} tokens (~${Math.floor(rawConfig.llm.eventDescriptionTokensLimit / 4)} words or ~${rawConfig.llm.eventDescriptionTokensLimit * 4} characters)`,
  },
};

export const config = {
  ...rawConfig,
  userInputLimits,
  eventDescriptionGuidance,
};
