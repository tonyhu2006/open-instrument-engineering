import { useEffect, useMemo, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Edit, Trash2, Power, PowerOff } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
  userApi,
  roleApi,
  organizationCrudApi,
  type UserProfile,
  type Role,
  type Organization,
} from '@/lib/api'
import { AdminTable, type AdminColumn } from './components/AdminTable'
import { AdminPageHeader } from './components/AdminPageHeader'

interface UserFormState extends Partial<UserProfile> {
  password?: string
  password_confirm?: string
}

export function UsersPage() {
  return (
    <RoleGuard require="canManageUsers">
      <UsersPageInner />
    </RoleGuard>
  )
}

function UsersPageInner() {
  const { t } = useTranslation()
  const [data, setData] = useState<UserProfile[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [orgs, setOrgs] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<UserFormState | null>(null)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [u, r, o] = await Promise.all([
        userApi.list(),
        roleApi.list().catch(() => [] as Role[]),
        organizationCrudApi.list().catch(() => [] as Organization[]),
      ])
      setData(u)
      setRoles(r)
      setOrgs(o)
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return data
    return data.filter(
      (u) =>
        u.username.toLowerCase().includes(q) ||
        u.email.toLowerCase().includes(q) ||
        (u.full_name ?? '').toLowerCase().includes(q),
    )
  }, [data, search])

  const handleSave = async () => {
    if (!editing) return
    if (!editing.id && !editing.password) {
      alert(t('users.errors.passwordRequired'))
      return
    }
    if (editing.password && editing.password !== editing.password_confirm) {
      alert(t('users.errors.passwordMismatch'))
      return
    }
    setSaving(true)
    try {
      const payload: UserFormState = { ...editing }
      if (editing.id) {
        // Passwords change only through POST /users/{id}/reset-password/ (§15.7)
        const newPassword = payload.password
        delete payload.password
        delete payload.password_confirm
        await userApi.update(editing.id, payload)
        if (newPassword) {
          await userApi.resetPassword(editing.id, newPassword, editing.password_confirm ?? '')
        }
      } else {
        await userApi.create(payload)
      }
      setEditing(null)
      await load()
    } catch (e: unknown) {
      alert(`${t('common.saveFailed')}: ${apiErrorMessage(e)}`)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (u: UserProfile) => {
    if (!confirm(`${t('common.confirmDelete')} "${u.username}"?`)) return
    try {
      await userApi.delete(u.id)
      await load()
    } catch (e: unknown) {
      alert(`${t('common.deleteFailed')}: ${apiErrorMessage(e)}`)
    }
  }

  const handleToggle = async (u: UserProfile) => {
    try {
      if (u.is_active) await userApi.deactivate(u.id)
      else await userApi.activate(u.id)
      await load()
    } catch (e) {
      alert(`${t('users.actions.toggleFailed')}: ${e instanceof Error ? e.message : ''}`)
    }
  }

  const columns: AdminColumn<UserProfile>[] = [
    {
      key: 'username',
      header: t('users.columns.username'),
      render: (r) => <span className="font-mono">{r.username}</span>,
    },
    { key: 'full_name', header: t('users.columns.fullName') },
    { key: 'email', header: t('users.columns.email') },
    {
      key: 'role_name',
      header: t('users.columns.role'),
      render: (r) =>
        r.role_name ? (
          <Badge variant="outline">
            {r.role_name} <span className="ml-1 text-xs opacity-70">L{r.role_level}</span>
          </Badge>
        ) : (
          '—'
        ),
    },
    {
      key: 'organization_name',
      header: t('users.columns.organization'),
      render: (r) => r.organization_name || '—',
    },
    {
      key: 'is_active',
      header: t('users.columns.status'),
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
        title={t('users.title')}
        description={t('users.description')}
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder={t('users.searchPlaceholder')}
        onRefresh={load}
        onCreate={() =>
          setEditing({
            username: '',
            email: '',
            first_name: '',
            last_name: '',
            password: '',
            password_confirm: '',
            is_active: true,
          })
        }
        createLabel={t('users.createLabel')}
      />

      <AdminTable
        storageKey="admin.users"
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
              onClick={() => handleToggle(r)}
              title={r.is_active ? t('users.actions.deactivate') : t('users.actions.activate')}
            >
              {r.is_active ? <PowerOff className="h-4 w-4" /> : <Power className="h-4 w-4" />}
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={async () => {
                try {
                  // List endpoint returns a lightweight serializer; fetch the
                  // full record so the edit form can populate every field.
                  const full = await userApi.get(r.id)
                  setEditing(full)
                } catch (e) {
                  console.error('Failed to load user for editing:', e)
                  setEditing(r)
                }
              }}
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
              <DialogTitle>{editing.id ? t('users.editTitle') : t('users.createTitle')}</DialogTitle>
              <DialogDescription>{t('users.dialogDescription')}</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label>
                    {t('users.fields.username')} {t('common.required')}
                  </Label>
                  <Input
                    value={editing.username ?? ''}
                    onChange={(e) => setEditing({ ...editing, username: e.target.value })}
                    disabled={!!editing.id}
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label>{t('users.fields.email')}</Label>
                  <Input
                    type="email"
                    value={editing.email ?? ''}
                    onChange={(e) => setEditing({ ...editing, email: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label>{t('users.fields.firstName')}</Label>
                  <Input
                    value={editing.first_name ?? ''}
                    onChange={(e) => setEditing({ ...editing, first_name: e.target.value })}
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label>{t('users.fields.lastName')}</Label>
                  <Input
                    value={editing.last_name ?? ''}
                    onChange={(e) => setEditing({ ...editing, last_name: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label>
                    {t('users.fields.password')}{' '}
                    {editing.id ? t('users.passwordHintEdit') : t('common.required')}
                  </Label>
                  <Input
                    type="password"
                    autoComplete="new-password"
                    value={editing.password ?? ''}
                    onChange={(e) => setEditing({ ...editing, password: e.target.value })}
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label>
                    {t('users.fields.passwordConfirm')} {editing.id ? '' : t('common.required')}
                  </Label>
                  <Input
                    type="password"
                    autoComplete="new-password"
                    value={editing.password_confirm ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, password_confirm: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label>{t('users.fields.organization')}</Label>
                  <Select
                    value={editing.organization ?? ''}
                    onChange={(e) =>
                      setEditing({
                        ...editing,
                        organization: e.target.value ? Number(e.target.value) : null,
                      })
                    }
                  >
                    <option value="">{t('users.selectPlaceholder')}</option>
                    {orgs.map((o) => (
                      <option key={o.id} value={o.id}>
                        {o.code} - {o.name}
                      </option>
                    ))}
                  </Select>
                </div>
                <div className="grid gap-1.5">
                  <Label>{t('users.fields.role')}</Label>
                  <Select
                    value={editing.role ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, role: e.target.value ? Number(e.target.value) : null })
                    }
                  >
                    <option value="">{t('users.selectPlaceholder')}</option>
                    {roles.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name} (L{r.level})
                      </option>
                    ))}
                  </Select>
                </div>
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={editing.is_active ?? true}
                  onChange={(e) => setEditing({ ...editing, is_active: e.target.checked })}
                />
                {t('users.fields.isActive')}
              </label>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditing(null)} disabled={saving}>
                {t('common.cancel')}
              </Button>
              <Button onClick={handleSave} disabled={saving || !editing.username}>
                {saving ? t('common.saving') : t('common.save')}
              </Button>
            </DialogFooter>
          </>
        )}
      </Dialog>
    </div>
  )
}
