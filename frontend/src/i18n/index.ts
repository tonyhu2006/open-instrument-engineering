import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import enUS from './locales/en-US.json'
import zhCN from './locales/zh-CN.json'

/**
 * OpenInstrument i18n configuration.
 *
 * Per SPECIFICATION.md §3.9 — English (en-US) is the primary language.
 * All UI source strings are written in English; other languages are
 * provided as translation bundles. Source code MUST NOT contain
 * non-English literals in user-visible places.
 *
 * Currently supported:
 *  - en-US (primary, complete)
 *  - zh-CN (placeholder for future translation)
 *
 * Planned expansion (per spec §3.9.1):
 *  East Asia: zh-TW, ja, ko
 *  Europe:    fr, es, it, de, ru
 *  RTL:       ar, he
 */

export const SUPPORTED_LANGUAGES = [
  { code: 'en-US', label: 'English' },
  { code: 'zh-CN', label: '简体中文' },
] as const

export const DEFAULT_LANGUAGE = 'en-US'

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      'en-US': { translation: enUS },
      'zh-CN': { translation: zhCN },
    },
    fallbackLng: DEFAULT_LANGUAGE,
    lng: DEFAULT_LANGUAGE,
    interpolation: {
      escapeValue: false, // React already escapes
    },
    detection: {
      order: ['localStorage', 'navigator'],
      lookupLocalStorage: 'openinstrument.lang',
      caches: ['localStorage'],
    },
    returnNull: false,
  })

export default i18n
