import { useCallback, useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Badge } from '@/components/ui/badge'
import { RoleGuard } from '@/components/auth'
import { auditLogApi, type AuditLog } from '@/lib/api'
import { AdminTable, type AdminColumn } from './components/AdminTable'
import { AdminPageHeader } from './components/AdminPageHeader'

export function AuditLogsPage() {
  return (
    <RoleGuard require="canViewAuditLogs">
      <AuditLogsPageInner />
    </RoleGuard>
  )
}

function AuditLogsPageInner() {
  const { t, i18n } = useTranslation()
  const [data, setData] = useState<AuditLog[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await auditLogApi.list())
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.loadFailed'))
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    load()
  }, [load])

  const actionColor = (action: string) => {
    switch (action.toUpperCase()) {
      case 'CREATE':
        return 'bg-green-500/10 text-green-700 border-green-500/30'
      case 'UPDATE':
        return 'bg-blue-500/10 text-blue-700 border-blue-500/30'
      case 'DELETE':
        return 'bg-red-500/10 text-red-700 border-red-500/30'
      default:
        return 'bg-muted text-muted-foreground'
    }
  }

  const columns: AdminColumn<AuditLog>[] = [
    {
      key: 'timestamp',
      header: t('auditLogs.columns.timestamp'),
      width: '180px',
      render: (r) => (
        <span className="font-mono text-xs">
          {new Date(r.timestamp).toLocaleString(i18n.language)}
        </span>
      ),
    },
    {
      key: 'user_name',
      header: t('auditLogs.columns.user'),
      width: '140px',
      render: (r) => r.user_name || t('auditLogs.systemUser'),
    },
    {
      key: 'action',
      header: t('auditLogs.columns.action'),
      width: '100px',
      render: (r) => (
        <span
          className={`inline-flex rounded border px-2 py-0.5 text-xs font-medium ${actionColor(r.action)}`}
        >
          {r.action}
        </span>
      ),
    },
    {
      key: 'model_name',
      header: t('auditLogs.columns.model'),
      width: '160px',
      render: (r) => <Badge variant="outline">{r.model_name}</Badge>,
    },
    {
      key: 'object_repr',
      header: t('auditLogs.columns.object'),
      render: (r) => <span className="line-clamp-1">{r.object_repr || `#${r.object_id}`}</span>,
    },
    {
      key: 'ip_address',
      header: t('auditLogs.columns.ipAddress'),
      width: '120px',
      render: (r) => <span className="font-mono text-xs">{r.ip_address || '—'}</span>,
    },
  ]

  return (
    <div>
      <AdminPageHeader
        title={t('auditLogs.title')}
        description={t('auditLogs.description')}
        onRefresh={load}
      />
      <AdminTable
        storageKey="admin.auditLogs"
        data={data}
        columns={columns}
        loading={loading}
        error={error}
        rowKey={(r) => r.id}
      />
    </div>
  )
}
