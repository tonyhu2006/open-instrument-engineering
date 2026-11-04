import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { healthCheck, type HealthCheckResponse } from '@/lib/api'
import { Activity, Database, Server, Wifi } from 'lucide-react'

export function Dashboard() {
  const { t } = useTranslation()
  const [health, setHealth] = useState<HealthCheckResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setLoading(true)
        const data = await healthCheck()
        setHealth(data)
        setError(null)
      } catch (err) {
        setError(t('dashboard.errorConnect'))
        console.error('Health check failed:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchHealth()
    const interval = setInterval(fetchHealth, 30000)
    return () => clearInterval(interval)
  }, [t])

  const getStatusBadge = (status: string) => {
    if (status === 'connected' || status === 'healthy') {
      return <Badge variant="success">{t('dashboard.badge.connected')}</Badge>
    }
    if (status.startsWith('error')) {
      return <Badge variant="destructive">{t('dashboard.badge.error')}</Badge>
    }
    return <Badge variant="warning">{t('dashboard.badge.unknown')}</Badge>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">{t('dashboard.title')}</h1>
        <p className="text-muted-foreground">{t('dashboard.welcome')}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.card.apiStatus')}</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold">{t('dashboard.loading')}</div>
            ) : error ? (
              <div className="space-y-1">
                <div className="text-2xl font-bold text-destructive">{t('dashboard.badge.offline')}</div>
                <p className="text-xs text-muted-foreground">{error}</p>
              </div>
            ) : (
              <div className="space-y-1">
                <div className="text-2xl font-bold">{health?.status}</div>
                <p className="text-xs text-muted-foreground">
                  {t('dashboard.version', { version: health?.version ?? '-' })}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.card.database')}</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold">{t('dashboard.badge.checking')}</div>
            ) : (
              <div className="space-y-1">
                {getStatusBadge(health?.services.database || 'unknown')}
                <p className="text-xs text-muted-foreground mt-2">PostgreSQL</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.card.cache')}</CardTitle>
            <Wifi className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold">{t('dashboard.badge.checking')}</div>
            ) : (
              <div className="space-y-1">
                {getStatusBadge(health?.services.cache || 'unknown')}
                <p className="text-xs text-muted-foreground mt-2">Redis</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">{t('dashboard.card.healthCheck')}</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {loading ? (
                <Badge variant="secondary">{t('dashboard.badge.checking')}</Badge>
              ) : error ? (
                <Badge variant="destructive">{t('dashboard.badge.failed')}</Badge>
              ) : (
                <Badge variant="success">{t('dashboard.badge.passed')}</Badge>
              )}
              <p className="text-xs text-muted-foreground mt-2">{t('dashboard.autoRefresh')}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.card.quickStart')}</CardTitle>
            <CardDescription>{t('dashboard.card.quickStartDesc')}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-2">
                <Database className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h4 className="font-medium">{t('dashboard.quickStep.hierarchy')}</h4>
                <p className="text-sm text-muted-foreground">{t('dashboard.quickStep.hierarchyDesc')}</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-2">
                <Activity className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h4 className="font-medium">{t('dashboard.quickStep.tags')}</h4>
                <p className="text-sm text-muted-foreground">{t('dashboard.quickStep.tagsDesc')}</p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-2">
                <Server className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h4 className="font-medium">{t('dashboard.quickStep.loops')}</h4>
                <p className="text-sm text-muted-foreground">{t('dashboard.quickStep.loopsDesc')}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('dashboard.card.systemInfo')}</CardTitle>
            <CardDescription>{t('dashboard.card.systemInfoDesc')}</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t('dashboard.info.apiEndpoint')}</span>
                <span className="font-mono">/api/</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t('dashboard.info.healthCheck')}</span>
                <span className="font-mono">/api/health/</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t('dashboard.info.apiDocs')}</span>
                <span className="font-mono">/api/docs/</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t('dashboard.info.backendPort')}</span>
                <span className="font-mono">8000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t('dashboard.info.frontendPort')}</span>
                <span className="font-mono">5173</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
