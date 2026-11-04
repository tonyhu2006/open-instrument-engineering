import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Globe, User, Bell, SlidersHorizontal } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { SUPPORTED_LANGUAGES } from '@/i18n'
import { cn } from '@/lib/utils'

type TabKey = 'general' | 'account' | 'notifications' | 'advanced'

interface TabDef {
  key: TabKey
  icon: React.ComponentType<{ className?: string }>
  enabled: boolean
}

const TABS: TabDef[] = [
  { key: 'general', icon: SlidersHorizontal, enabled: true },
  { key: 'account', icon: User, enabled: false },
  { key: 'notifications', icon: Bell, enabled: false },
  { key: 'advanced', icon: SlidersHorizontal, enabled: false },
]

export function SettingsPage() {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<TabKey>('general')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('settings.title')}</h1>
        <p className="text-muted-foreground">{t('settings.subtitle')}</p>
      </div>

      {/* Tab nav */}
      <div className="border-b">
        <nav className="-mb-px flex gap-4" role="tablist">
          {TABS.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.key
            return (
              <button
                key={tab.key}
                role="tab"
                aria-selected={isActive}
                onClick={() => setActiveTab(tab.key)}
                className={cn(
                  'inline-flex items-center gap-2 border-b-2 px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'border-primary text-foreground'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/30',
                )}
              >
                <Icon className="h-4 w-4" />
                {t(`settings.tab.${tab.key}`)}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab content */}
      {activeTab === 'general' && <GeneralTab />}
      {activeTab === 'account' && (
        <PlaceholderPanel text={t('settings.placeholder.account')} />
      )}
      {activeTab === 'notifications' && (
        <PlaceholderPanel text={t('settings.placeholder.notifications')} />
      )}
      {activeTab === 'advanced' && (
        <PlaceholderPanel text={t('settings.placeholder.advanced')} />
      )}
    </div>
  )
}

function GeneralTab() {
  const { t, i18n } = useTranslation()
  const [status, setStatus] = useState<string | null>(null)

  const currentLang = i18n.resolvedLanguage ?? i18n.language ?? 'en-US'
  const currentLabel =
    SUPPORTED_LANGUAGES.find((l) => l.code === currentLang)?.label ?? currentLang

  const handleChange = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const next = e.target.value
    await i18n.changeLanguage(next)
    // LanguageDetector's `caches: ['localStorage']` already persists; guard anyway.
    try {
      window.localStorage.setItem('openinstrument.lang', next)
    } catch {
      /* ignore storage errors */
    }
    const label =
      SUPPORTED_LANGUAGES.find((l) => l.code === next)?.label ?? next
    setStatus(label)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Globe className="h-5 w-5" />
          {t('settings.language.title')}
        </CardTitle>
        <CardDescription>{t('settings.language.description')}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="grid max-w-xs gap-1.5">
          <Label htmlFor="settings-language">{t('settings.language.label')}</Label>
          <Select
            id="settings-language"
            value={currentLang}
            onChange={handleChange}
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.label}
              </option>
            ))}
          </Select>
        </div>
        <p className="text-xs text-muted-foreground">
          {t('settings.language.current', { lang: currentLabel })}
        </p>
        {status && (
          <p className="text-xs text-emerald-600 dark:text-emerald-400">
            {t('settings.language.applied', { lang: status })}
          </p>
        )}
      </CardContent>
    </Card>
  )
}

function PlaceholderPanel({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-dashed p-8 text-center text-sm text-muted-foreground">
      {text}
    </div>
  )
}
