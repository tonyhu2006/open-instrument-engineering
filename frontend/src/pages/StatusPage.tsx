import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { healthCheck, type HealthCheckResponse } from '@/lib/api'
import { RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react'

export function StatusPage() {
  const [health, setHealth] = useState<HealthCheckResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastChecked, setLastChecked] = useState<Date | null>(null)

  const fetchHealth = async () => {
    try {
      setLoading(true)
      const data = await healthCheck()
      setHealth(data)
      setError(null)
      setLastChecked(new Date())
    } catch (err) {
      setError('Failed to connect to backend API')
      console.error('Health check failed:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHealth()
  }, [])

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
      return <Badge variant="success">Healthy</Badge>
    }
    if (status.startsWith('error')) {
      return <Badge variant="destructive">Error</Badge>
    }
    return <Badge variant="warning">Unknown</Badge>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">System Status</h1>
          <p className="text-muted-foreground">
            Monitor the health of all system components
          </p>
        </div>
        <Button onClick={fetchHealth} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {lastChecked && (
        <p className="text-sm text-muted-foreground">
          Last checked: {lastChecked.toLocaleTimeString()}
        </p>
      )}

      {error && (
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive flex items-center gap-2">
              <XCircle className="h-5 w-5" />
              Connection Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <p className="text-sm text-muted-foreground mt-2">
              Make sure the backend server is running on port 8000
            </p>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              API Server
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
              ) : error ? (
                <XCircle className="h-5 w-5 text-red-500" />
              ) : (
                getStatusIcon(health?.status || 'unknown')
              )}
            </CardTitle>
            <CardDescription>Django REST Framework</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>Status</span>
                {loading ? (
                  <Badge variant="secondary">Checking...</Badge>
                ) : error ? (
                  <Badge variant="destructive">Offline</Badge>
                ) : (
                  getStatusBadge(health?.status || 'unknown')
                )}
              </div>
              <div className="flex justify-between items-center">
                <span>Version</span>
                <span className="font-mono text-sm">{health?.version || '-'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Database
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
              ) : (
                getStatusIcon(health?.services.database || 'unknown')
              )}
            </CardTitle>
            <CardDescription>PostgreSQL 16</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>Status</span>
                {loading ? (
                  <Badge variant="secondary">Checking...</Badge>
                ) : (
                  getStatusBadge(health?.services.database || 'unknown')
                )}
              </div>
              <div className="flex justify-between items-center">
                <span>Port</span>
                <span className="font-mono text-sm">5432</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              Cache
              {loading ? (
                <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
              ) : (
                getStatusIcon(health?.services.cache || 'unknown')
              )}
            </CardTitle>
            <CardDescription>Redis 7</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span>Status</span>
                {loading ? (
                  <Badge variant="secondary">Checking...</Badge>
                ) : (
                  getStatusBadge(health?.services.cache || 'unknown')
                )}
              </div>
              <div className="flex justify-between items-center">
                <span>Port</span>
                <span className="font-mono text-sm">6379</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
