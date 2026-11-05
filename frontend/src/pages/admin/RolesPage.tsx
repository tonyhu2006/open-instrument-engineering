import { useCallback, useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Edit, Trash2, Lock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select } from '@/components/ui/select'
import {
  Dialog,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog'
import { RoleGuard } from '@/components/auth'
import {
  apiErrorMessage,
  roleApi,
  organizationCrudApi,
  type Role,
  type Organization,
} from '@/lib/api'
import { AdminTable, type AdminColumn } from './components/AdminTable'
import { AdminPageHeader } from './components/AdminPageHeader'

const LEVEL_VALUES = [5, 4, 3, 2, 1] as const

export function RolesPage() {
  return (
    <RoleGuard require="canManageUsers">
      <RolesPageInner />
    </RoleGuard>
  )
}

function RolesPageInner() {
  const { t } = useTranslation()
  const [data, setData] = useState<Role[]>([])
  const [orgs, setOrgs] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<Partial<Role> | null>(null)
  const [saving, setSaving] = useState(false)
  const [permJson, setPermJson] = useState('{}')

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [r, o] = await Promise.all([
        roleApi.list(),
        organizationCrudApi.list().catch(() => [] as Organization[]),
      ])
      setData(r)
      setOrgs(o)
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.loadFailed'))
    } finally {
      setLoading(false)
    }
  }, [t])

  useEffect(() => {
    load()
  }, [load])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return data
    return data.filter(
      (r) => r.code.toLowerCase().includes(q) || r.name.toLowerCase().includes(q),
    )
  }, [data, search])

  const openEditor = (r: Partial<Role> | null) => {
    setEditing(
      r ?? {
        code: '',
        name: '',
        level: 1,
        description: '',
        permissions: {},
        is_system_role: false,
      },
    )
    setPermJson(JSON.stringify(r?.permissions ?? {}, null, 2))
  }

  const handleSave = async () => {
    if (!editing) return
    setSaving(true)
    try {
      let permissions: Record<string, string[]> = {}
      try {
        permissions = permJson.trim() ? JSON.parse(permJson) : {}
      } catch {
        alert(t('roles.errors.permissionsJson'))
        setSaving(false)
        return
      }
      const payload = { ...editing, permissions }
      if (editing.id) {
        await roleApi.update(editing.id, payload)
      } else {
        await roleApi.create(payload)
      }
      setEditing(null)
      await load()
    } catch (e: unknown) {
      alert(`${t('common.saveFailed')}: ${apiErrorMessage(e)}`)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (r: Role) => {
    if (r.is_system_role) {
      alert(t('roles.errors.systemRoleProtected'))
      return
    }
    if (!confirm(`${t('common.confirmDelete')} "${r.name}"?`)) return
    try {
      await roleApi.delete(r.id)
      await load()
    } catch (e: unknown) {
      alert(`${t('common.deleteFailed')}: ${apiErrorMessage(e)}`)
    }
  }

  const columns: AdminColumn<Role>[] = [
    {
      key: 'code',
      header: t('roles.columns.code'),
      width: '160px',
      render: (r) => <span className="font-mono text-xs">{r.code}</span>,
    },
    { key: 'name', header: t('roles.columns.name') },
    {
      key: 'level',
      header: t('roles.columns.level'),
      width: '100px',
      render: (r) => (
        <Badge variant={r.level >= 4 ? 'default' : 'outline'}>L{r.level}</Badge>
      ),
    },
    {
      key: 'organization_name',
      header: t('roles.columns.organization'),
      render: (r) => r.organization_name || '—',
    },
    {
      key: 'is_system_role',
      header: t('roles.columns.type'),
      width: '100px',
      render: (r) =>
        r.is_system_role ? (
          <Badge variant="secondary" className="gap-1">
            <Lock className="h-3 w-3" /> {t('roles.type.system')}
          </Badge>
        ) : (
          <Badge variant="outline">{t('roles.type.custom')}</Badge>
        ),
    },
  ]

  return (
    <div>
      <AdminPageHeader
        title={t('roles.title')}
        description={t('roles.description')}
        searchValue={search}
        onSearchChange={setSearch}
        onRefresh={load}
        onCreate={() => openEditor(null)}
        createLabel={t('roles.createLabel')}
      />

      <AdminTable
        storageKey="admin.roles"
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
              onClick={() => openEditor(r)}
              title={t('common.edit')}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleDelete(r)}
              title={t('common.delete')}
              disabled={r.is_system_role}
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
                {editing.id ? t('roles.editTitle') : t('roles.createTitle')}
              </DialogTitle>
              <DialogDescription>{t('roles.dialogDescription')}</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label>
                    {t('roles.fields.code')} {t('common.required')}
                  </Label>
                  <Input
                    value={editing.code ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, code: e.target.value.toUpperCase() })
                    }
                    placeholder="e.g. INST_ENG"
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label>
                    {t('roles.fields.name')} {t('common.required')}
                  </Label>
                  <Input
                    value={editing.name ?? ''}
                    onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label>
                    {t('roles.fields.organization')} {t('common.required')}
                  </Label>
                  <Select
                    value={editing.organization ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, organization: Number(e.target.value) })
                    }
                  >
                    <option value="">{t('roles.selectOrgPlaceholder')}</option>
                    {orgs.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.code} - {o.name}
                      </option>
                    ))}
                  </Select>
                </div>
                <div className="grid gap-1.5">
                  <Label>
                    {t('roles.fields.level')} {t('common.required')}
                  </Label>
                  <Select
                    value={editing.level ?? 1}
                    onChange={(e) =>
                      setEditing({ ...editing, level: Number(e.target.value) })
                    }
                  >
                    {LEVEL_VALUES.map((v) => (
                      <option key={v} value={v}>
                        {t(`roles.levelOption.${v}`)}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>
              <div className="grid gap-1.5">
                <Label>{t('roles.fields.description')}</Label>
                <Textarea
                  value={editing.description ?? ''}
                  onChange={(e) => setEditing({ ...editing, description: e.target.value })}
                />
              </div>
              <div className="grid gap-1.5">
                <Label>{t('roles.fields.permissions')}</Label>
                <Textarea
                  value={permJson}
                  onChange={(e) => setPermJson(e.target.value)}
                  rows={6}
                  className="font-mono text-xs"
                  placeholder='{"tag":["create","read","update"],"loop":["read"]}'
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditing(null)} disabled={saving}>
                {t('common.cancel')}
              </Button>
              <Button
                onClick={handleSave}
                disabled={saving || !editing.code || !editing.name || !editing.organization}
              >
                {saving ? t('common.saving') : t('common.save')}
              </Button>
            </DialogFooter>
          </>
        )}
      </Dialog>
    </div>
  )
}
