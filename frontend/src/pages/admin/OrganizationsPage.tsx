import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Edit, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { RoleGuard } from '@/components/auth'
import { organizationCrudApi, type Organization } from '@/lib/api'
import { AdminTable, type AdminColumn } from './components/AdminTable'
import { AdminPageHeader } from './components/AdminPageHeader'

export function OrganizationsPage() {
  return (
    <RoleGuard require="canManageUsers">
      <OrganizationsPageInner />
    </RoleGuard>
  )
}

function OrganizationsPageInner() {
  const { t } = useTranslation()
  const [data, setData] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<Partial<Organization> | null>(null)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setData(await organizationCrudApi.list())
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return data
    return data.filter(
      (o) => o.code.toLowerCase().includes(q) || o.name.toLowerCase().includes(q),
    )
  }, [data, search])

  const handleSave = async () => {
    if (!editing) return
    setSaving(true)
    try {
      if (editing.id) {
        await organizationCrudApi.update(editing.id, editing)
      } else {
        await organizationCrudApi.create(editing)
      }
      setEditing(null)
      await load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: unknown } }
      alert(`${t('common.saveFailed')}: ${JSON.stringify(err.response?.data ?? e)}`)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (org: Organization) => {
    if (!confirm(t('common.confirmDelete') + ` "${org.name}"?`)) return
    try {
      await organizationCrudApi.delete(org.id)
      await load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: unknown } }
      alert(`${t('common.deleteFailed')}: ${JSON.stringify(err.response?.data ?? e)}`)
    }
  }

  const columns: AdminColumn<Organization>[] = [
    {
      key: 'code',
      header: t('common.code'),
      width: '120px',
      render: (r) => <span className="font-mono">{r.code}</span>,
    },
    { key: 'name', header: t('common.name') },
    {
      key: 'description',
      header: t('common.description'),
      render: (r) => (
        <span className="line-clamp-1 text-muted-foreground">{r.description || '—'}</span>
      ),
    },
    {
      key: 'is_active',
      header: t('common.status'),
      width: '80px',
      render: (r) => (
        <Badge variant={r.is_active ? 'default' : 'secondary'}>
          {r.is_active ? t('common.enabled') : t('common.disabled')}
        </Badge>
      ),
    },
  ]

  return (
    <div>
      <AdminPageHeader
        title={t('organizations.title')}
        description={t('organizations.description')}
        searchValue={search}
        onSearchChange={setSearch}
        onRefresh={load}
        onCreate={() => setEditing({ code: '', name: '', description: '', is_active: true })}
        createLabel={t('organizations.createLabel')}
      />

      <AdminTable
        storageKey="admin.organizations"
        data={filtered}
        columns={columns}
        loading={loading}
        error={error}
        rowKey={(r) => r.id}
        actions={(r) => (
          <>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setEditing(r)}
              title={t('common.edit')}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleDelete(r)}
              title={t('common.delete')}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </>
        )}
      />

      <Dialog open={!!editing} onOpenChange={(o) => !o && setEditing(null)}>
        {editing && (
          <>
            <DialogHeader>
              <DialogTitle>
                {editing.id ? t('organizations.editTitle') : t('organizations.createTitle')}
              </DialogTitle>
              <DialogDescription>
                {editing.id
                  ? t('organizations.editDescription')
                  : t('organizations.createDescription')}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4">
              <div className="grid gap-1.5">
                <Label htmlFor="org-code">
                  {t('organizations.fields.code')} {t('common.required')}
                </Label>
                <Input
                  id="org-code"
                  value={editing.code ?? ''}
                  onChange={(e) =>
                    setEditing({ ...editing, code: e.target.value.toUpperCase() })
                  }
                  placeholder="e.g. SINOPEC"
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="org-name">
                  {t('organizations.fields.name')} {t('common.required')}
                </Label>
                <Input
                  id="org-name"
                  value={editing.name ?? ''}
                  onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="org-desc">{t('organizations.fields.description')}</Label>
                <Textarea
                  id="org-desc"
                  value={editing.description ?? ''}
                  onChange={(e) => setEditing({ ...editing, description: e.target.value })}
                />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={editing.is_active ?? true}
                  onChange={(e) => setEditing({ ...editing, is_active: e.target.checked })}
                />
                {t('organizations.fields.isActive')}
              </label>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditing(null)} disabled={saving}>
                {t('common.cancel')}
              </Button>
              <Button onClick={handleSave} disabled={saving || !editing.code || !editing.name}>
                {saving ? t('common.saving') : t('common.save')}
              </Button>
            </DialogFooter>
          </>
        )}
      </Dialog>
    </div>
  )
}
