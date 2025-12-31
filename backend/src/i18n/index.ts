import i18next from 'i18next';
import FsBackend from 'i18next-fs-backend';
import { config } from '../config.ts';

let i18nInstance: typeof i18next | null = null;

export async function initializeI18n(): Promise<void> {
  if (i18nInstance) {
    return;
  }

  await i18next.use(FsBackend).init({
    lng: config.defaultLanguage,
    fallbackLng: 'en',
    ns: ['common', 'game', 'prompts'],
    defaultNS: 'common',
    backend: {
      loadPath: new URL('./locales/{{lng}}/{{ns}}.json', import.meta.url).pathname,
    },
    interpolation: {
      escapeValue: false,
    },
  });

  i18nInstance = i18next;
}

export function getI18n() {
  if (!i18nInstance) {
    throw new Error('i18n not initialized. Call initializeI18n() first.');
  }
  return i18nInstance;
}

export function createNamespacedTranslator(language: string, namespace: string) {
  const instance = getI18n();
  return (key: string, defaultValue?: string, options?: Record<string, any>) => {
    return instance.t(`${key}`, {
      lng: language,
      ns: namespace,
      defaultValue,
      ...options,
    });
  };
}
