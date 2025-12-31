import i18next from 'i18next';
import FsBackend from 'i18next-fs-backend';
import { config } from '../config.ts';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

let i18nInstance: typeof i18next | null = null;

export async function initializeI18n(): Promise<void> {
  if (i18nInstance) {
    return;
  }

  // Get the directory of the current module
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);
  const localesPath = join(__dirname, 'locales', '{{lng}}', '{{ns}}.json');

  await i18next.use(FsBackend).init({
    lng: config.defaultLanguage,
    fallbackLng: 'en',
    supportedLngs: ['en', 'zh'],
    preload: ['en', 'zh'], // Preload all supported languages
    ns: ['common', 'game', 'prompts'],
    defaultNS: 'common',
    backend: {
      loadPath: localesPath,
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
