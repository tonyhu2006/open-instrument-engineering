import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { healthCheck, type HealthCheckResponse } from '@/lib/api'
import { Activity, Database, Server, Wifi } from 'lucide-react'

export function Dashboard() {
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
        setError('Failed to connect to backend API')
        console.error('Health check failed:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchHealth()
    const interval = setInterval(fetchHealth, 30000)
    return () => clearInterval(interval)
  }, [])

  const getStatusBadge = (status: string) => {
    if (status === 'connected' || status === 'healthy') {
      return <Badge variant="success">Connected</Badge>
    }
    if (status.startsWith('error')) {
      return <Badge variant="destructive">Error</Badge>
    }
    return <Badge variant="warning">Unknown</Badge>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to OpenInstrument - AI-Driven Instrumentation Design Platform
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Status</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold">Loading...</div>
            ) : error ? (
              <div className="space-y-1">
                <div className="text-2xl font-bold text-destructive">Offline</div>
                <p className="text-xs text-muted-foreground">{error}</p>
              </div>
            ) : (
              <div className="space-y-1">
                <div className="text-2xl font-bold">{health?.status}</div>
                <p className="text-xs text-muted-foreground">
                  Version: {health?.version}
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Database</CardTitle>
            <Database className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold">Checking...</div>
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
            <CardTitle className="text-sm font-medium">Cache</CardTitle>
            <Wifi className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="text-2xl font-bold">Checking...</div>
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
            <CardTitle className="text-sm font-medium">Health Check</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="space-y-1">
              {loading ? (
                <Badge variant="secondary">Checking...</Badge>
              ) : error ? (
                <Badge variant="destructive">Failed</Badge>
              ) : (
                <Badge variant="success">Passed</Badge>
              )}
              <p className="text-xs text-muted-foreground mt-2">
                Auto-refresh: 30s
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick Start</CardTitle>
            <CardDescription>
              Get started with OpenInstrument
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-2">
                <Database className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h4 className="font-medium">1. Set up Plant Hierarchy</h4>
                <p className="text-sm text-muted-foreground">
                  Define your Plant, Areas, and Units structure
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-2">
                <Activity className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h4 className="font-medium">2. Create Instrument Tags</h4>
                <p className="text-sm text-muted-foreground">
                  Add instruments to your Instrument Index
                </p>
              </div>
            </div>
            <div className="flex items-start gap-4">
              <div className="rounded-full bg-primary/10 p-2">
                <Server className="h-4 w-4 text-primary" />
              </div>
              <div>
                <h4 className="font-medium">3. Configure Loops</h4>
                <p className="text-sm text-muted-foreground">
                  Group instruments into control loops
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Information</CardTitle>
            <CardDescription>
              Backend API connection details
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">API Endpoint</span>
                <span className="font-mono">/api/</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Health Check</span>
                <span className="font-mono">/api/health/</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">API Docs</span>
                <span className="font-mono">/api/docs/</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Backend Port</span>
                <span className="font-mono">8000</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Frontend Port</span>
                <span className="font-mono">5173</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
