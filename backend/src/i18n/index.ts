import i18next from 'i18next';
import FsBackend from 'i18next-fs-backend';
import { config } from '../config.ts';
import { join, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';

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

  // Post-process to load @file: references
  loadFileReferences();

  i18nInstance = i18next;
}

/**
 * Post-processor to replace @file: references with actual file contents
 * Recursively traverses all translation resources and replaces strings starting with @file:
 */
function loadFileReferences(): void {
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);
  const localesDir = join(__dirname, 'locales');

  // Get all loaded resources from i18next
  const resources = i18next.store.data;

  for (const lang in resources) {
    for (const ns in resources[lang]) {
      const namespace = resources[lang][ns];
      processNamespace(namespace, join(localesDir, lang));
    }
  }
}

/**
 * Recursively process a namespace object and replace @file: references
 */
function processNamespace(obj: any, baseDir: string): void {
  if (!obj || typeof obj !== 'object') return;

  for (const key in obj) {
    const value = obj[key];

    if (typeof value === 'string' && value.startsWith('@file:')) {
      // Extract file path and load it
      const filePath = value.substring(6).trim(); // Remove "@file:" prefix
      const fullPath = resolve(baseDir, filePath);

      try {
        const fileContent = readFileSync(fullPath, 'utf-8');
        obj[key] = fileContent;
        console.log(`[i18n] Loaded file reference: @file:${filePath} -> ${fullPath}`);
      } catch (error) {
        console.error(`[i18n] Failed to load file: ${fullPath}`, error);
        // Keep the original value if file loading fails
      }
    } else if (typeof value === 'object') {
      // Recursively process nested objects
      processNamespace(value, baseDir);
    }
  }
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
