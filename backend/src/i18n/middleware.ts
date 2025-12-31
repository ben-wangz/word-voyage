import { Context as HonoContext, Next } from 'hono';
import { getI18n } from './index.ts';
import { config } from '../config.ts';

export interface I18nVariables {
  language: string;
  t: (key: string, defaultValue?: string, options?: Record<string, any>) => string;
}

export function i18nMiddleware() {
  return async (c: HonoContext, next: Next) => {
    const i18n = getI18n();

    // Language detection priority:
    // 1. Query parameter ?lang=zh or ?lang=en
    // 2. Accept-Language header
    // 3. Default language from config
    const queryLang = c.req.query('lang');
    const acceptLanguage = c.req.header('Accept-Language');

    let detectedLanguage = config.defaultLanguage;

    if (queryLang && (queryLang === 'en' || queryLang === 'zh')) {
      detectedLanguage = queryLang;
    } else if (acceptLanguage) {
      // Simple Accept-Language parsing (e.g., "zh-CN,zh;q=0.9,en;q=0.8")
      const firstLang = acceptLanguage.split(',')[0].split('-')[0].toLowerCase();
      if (firstLang === 'zh' || firstLang === 'en') {
        detectedLanguage = firstLang as 'en' | 'zh';
      }
    }

    // Create translation function bound to detected language
    const t = (key: string, defaultValue?: string, options?: Record<string, any>) => {
      return i18n.t(key, {
        lng: detectedLanguage,
        defaultValue,
        ...options,
      });
    };

    // Store language and translator in Hono context
    c.set('language', detectedLanguage);
    c.set('t', t);

    await next();
  };
}
