import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { healthCheck, type HealthCheckResponse } from '@/lib/api'
import { RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

export function StatusPage() {
  const { t, i18n } = useTranslation()
  const [health, setHealth] = useState<HealthCheckResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const fetchHealth = useCallback(async () => {
    try {
      setLoading(true)
      const data = await healthCheck()
      setHealth(data)
      setError(null)
      setLastChecked(new Date())
    } catch (err) {
      setError(t('statusPage.errorConnect'))
      console.error('Health check failed:', err)
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    fetchHealth()
  }, [fetchHealth])

  const getStatusIcon = (status: string) => {
    if (status === 'connected' || status === 'healthy') {
      return <CheckCircle className="h-5 w-5 text-green-500" />
    }
    if (status.startsWith('error')) {
      return <XCircle className="h-5 w-5 text-red-500" />
    }
    return <AlertCircle className="h-5 w-5 text-yellow-500" />
  }

  const getStatusBadge = (status: string) => {
    if (status === 'connected' || status === 'healthy') {
      return <Badge variant="success">{t('statusPage.badge.healthy')}</Badge>
    }
    if (status.startsWith('error')) {
      return <Badge variant="destructive">{t('statusPage.badge.error')}</Badge>
    }
    return <Badge variant="warning">{t('statusPage.badge.unknown')}</Badge>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('statusPage.title')}</h1>
          <p className="text-muted-foreground">{t('statusPage.subtitle')}</p>
        </div>
        <Button onClick={fetchHealth} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          {t('statusPage.refresh')}
        </Button>
      </div>

      {lastChecked && (
        <p className="text-sm text-muted-foreground">
          {t('statusPage.lastChecked', { time: lastChecked.toLocaleTimeString(i18n.language) })}
        </p>
      )}

      {error && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive flex items-center gap-2">
              <XCircle className="h-5 w-5" />
              {t('statusPage.connectionError')}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <p className="text-sm text-muted-foreground mt-2">{t('statusPage.errorDetail')}</p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              {t('statusPage.card.apiServer')}
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
              ) : error ? (
                <XCircle className="h-5 w-5 text-red-500" />
              ) : (
                getStatusIcon(health?.status || 'unknown')
              )}
            </CardTitle>
            <CardDescription>{t('statusPage.card.apiServerDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>{t('statusPage.field.status')}</span>
                {loading ? (
                  <Badge variant="secondary">{t('statusPage.badge.checking')}</Badge>
                ) : error ? (
                  <Badge variant="destructive">{t('statusPage.badge.offline')}</Badge>
                ) : (
                  getStatusBadge(health?.status || 'unknown')
                )}
              </div>
              <div className="flex justify-between items-center">
                <span>{t('statusPage.field.version')}</span>
                <span className="font-mono text-sm">{health?.version || '-'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              {t('statusPage.card.database')}
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
              ) : (
                getStatusIcon(health?.services.database || 'unknown')
              )}
            </CardTitle>
            <CardDescription>{t('statusPage.card.databaseDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>{t('statusPage.field.status')}</span>
                {loading ? (
                  <Badge variant="secondary">{t('statusPage.badge.checking')}</Badge>
                ) : (
                  getStatusBadge(health?.services.database || 'unknown')
                )}
              </div>
              <div className="flex justify-between items-center">
                <span>{t('statusPage.field.port')}</span>
                <span className="font-mono text-sm">5432</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              {t('statusPage.card.cache')}
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
              ) : (
                getStatusIcon(health?.services.cache || 'unknown')
              )}
            </CardTitle>
            <CardDescription>{t('statusPage.card.cacheDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>{t('statusPage.field.status')}</span>
                {loading ? (
                  <Badge variant="secondary">{t('statusPage.badge.checking')}</Badge>
                ) : (
                  getStatusBadge(health?.services.cache || 'unknown')
                )}
              </div>
              <div className="flex justify-between items-center">
                <span>{t('statusPage.field.port')}</span>
                <span className="font-mono text-sm">6379</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
