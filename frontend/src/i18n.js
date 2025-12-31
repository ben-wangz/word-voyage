import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import enLocale from './locales/en.json';
import zhLocale from './locales/zh.json';

// Get saved language from localStorage or browser preference
const getSavedLanguage = () => {
  const saved = localStorage.getItem('language');
  if (saved && (saved === 'en' || saved === 'zh')) {
    return saved;
  }

  // Check browser language
  const browserLang = navigator.language.split('-')[0];
  if (browserLang === 'zh') {
    return 'zh';
  }

  return 'en';
};

const defaultLanguage = getSavedLanguage();

i18next.use(initReactI18next).init({
  resources: {
    en: { translation: enLocale },
    zh: { translation: zhLocale },
  },
  lng: defaultLanguage,
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});

export default i18next;
