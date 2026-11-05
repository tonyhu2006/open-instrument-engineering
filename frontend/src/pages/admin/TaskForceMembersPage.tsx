import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  ArrowLeft,
  Loader2,
  AlertCircle,
  UserPlus,
  UserMinus,
  Users as UsersIcon,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { RoleGuard } from '@/components/auth'
import {
  apiErrorMessage,
  roleApi,
  taskForceApi,
  userApi,
  type ProjectTaskForce,
  type Role,
  type TaskForceMembership,
  type UserProfile,
} from '@/lib/api'
import { usePermissions } from '@/hooks/usePermissions'

export function TaskForceMembersPage() {
  return (
    <RoleGuard require="canManageTaskForces">
      <TaskForceMembersInner />
    </RoleGuard>
  )
}

function TaskForceMembersInner() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const taskForceId = Number(id)
  const perms = usePermissions()

  const [taskForce, setTaskForce] = useState<ProjectTaskForce | null>(null)
  const [members, setMembers] = useState<TaskForceMembership[]>([])
  const [users, setUsers] = useState<UserProfile[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  // §15.3.1 role_in_project: '' = keep the user's system role
  const [adding, setAdding] = useState<{ user_id: number | ''; role_in_project: number | '' }>({
    user_id: '',
    role_in_project: '',
  })
  const [busy, setBusy] = useState(false)

  const load = async () => {
    if (!taskForceId) return
    setLoading(true)
    setError(null)
    try {
      const [tf, mem, u, r] = await Promise.all([
        taskForceApi.get(taskForceId),
        taskForceApi.members(taskForceId),
        userApi.list().catch(() => [] as UserProfile[]),
        roleApi.list().catch(() => [] as Role[]),
      ])
      setTaskForce(tf)
      setMembers(mem)
      setUsers(u)
      setRoles(r)
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskForceId])

  const memberUserIds = useMemo(() => new Set(members.map((m) => m.user)), [members])
  const availableUsers = useMemo(
    () => users.filter((u) => !memberUserIds.has(u.id)),
    [users, memberUserIds],
  )

  const overrideCount = useMemo(
    () => members.filter((m) => m.role_in_project !== null).length,
    [members],
  )

  // ADM-TF01: Administrators manage any group, PM/PE only groups they created.
  const canEdit = !!taskForce && perms.canEditOwnTaskForce(taskForce.created_by)

  const handleAdd = async () => {
    if (!taskForce || !adding.user_id) return
    setBusy(true)
    try {
      await taskForceApi.addMember(
        taskForce.id,
        Number(adding.user_id),
        adding.role_in_project === '' ? null : Number(adding.role_in_project),
      )
      setAdding({ user_id: '', role_in_project: '' })
      setMembers(await taskForceApi.members(taskForce.id))
    } catch (e: unknown) {
      alert(`${t('common.saveFailed')}: ${apiErrorMessage(e)}`)
    } finally {
      setBusy(false)
    }
  }

  const handleRemove = async (m: TaskForceMembership) => {
    if (!taskForce) return
    if (!confirm(t('taskforce.members.removeConfirm'))) return
    setBusy(true)
    try {
      await taskForceApi.removeMember(taskForce.id, m.user)
      setMembers(await taskForceApi.members(taskForce.id))
    } catch (e) {
      alert(`${t('taskforce.errors.removeFailed')}: ${apiErrorMessage(e)}`)
    } finally {
      setBusy(false)
    }
  }

  if (loading) {
    return (
      <div className="flex h-60 items-center justify-center text-muted-foreground">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        {t('common.loading')}
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-60 flex-col items-center justify-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 text-destructive">
        <AlertCircle className="h-6 w-6" />
        <span className="text-sm">{error}</span>
        <Button variant="outline" size="sm" onClick={load}>
          {t('hierarchy.retry')}
        </Button>
      </div>
    )
  }

  if (!taskForce) {
    return (
      <div className="flex h-60 items-center justify-center text-muted-foreground">
        {t('taskforce.members.taskForceNotFound')}
      </div>
    )
  }

  const roleLabel = (m: TaskForceMembership) =>
    m.role_in_project_name ?? t('taskforce.members.roleOptions.system')

  return (
    <div className="space-y-4">
      {/* Breadcrumb / back */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <Link
            to="/admin/task-forces"
            className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            {t('taskforce.members.back')}
          </Link>
        </div>
        <div className="flex items-center gap-2 rounded-full border bg-background px-3 py-1.5 text-xs">
          <UsersIcon className="h-3.5 w-3.5" />
          <span className="font-mono">{taskForce.code}</span>
        </div>
      </div>

      {/* Task force header */}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="default" className="font-mono">
                {taskForce.code}
              </Badge>
              <h2 className="text-lg font-semibold">{taskForce.name}</h2>
              <Badge variant={taskForce.is_active ? 'default' : 'secondary'}>
                {taskForce.is_active ? t('common.enabled') : t('common.disabled')}
              </Badge>
            </div>
            {taskForce.description && (
              <p className="mt-1 text-sm text-muted-foreground">{taskForce.description}</p>
            )}
            <div className="mt-2 flex flex-wrap gap-4 text-xs text-muted-foreground">
              <span>
                {t('taskforce.columns.leader')}: {taskForce.leader_name ?? '—'}
              </span>
              <span>
                {t('taskforce.members.stat.total')}: {members.length}
              </span>
              <span>
                {t('taskforce.members.stat.overrides')}: {overrideCount}
              </span>
              <span>
                {t('taskforce.columns.createdBy')}: {taskForce.created_by_name ?? '—'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Add member form */}
      {canEdit && (
        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-3 text-sm font-medium">{t('taskforce.members.addTitle')}</h3>
          <div className="flex flex-wrap items-end gap-3">
            <div className="grid min-w-[240px] flex-1 gap-1.5">
              <Label className="text-xs">{t('common.user')}</Label>
              <Select
                value={adding.user_id}
                onChange={(e) =>
                  setAdding({
                    ...adding,
                    user_id: e.target.value ? Number(e.target.value) : '',
                  })
                }
                disabled={busy || availableUsers.length === 0}
              >
                <option value="">{t('taskforce.members.selectUser')}</option>
                {availableUsers.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.username}
                    {u.full_name ? ` — ${u.full_name}` : ''}
                  </option>
                ))}
              </Select>
            </div>
            <div className="grid w-60 gap-1.5">
              <Label className="text-xs">{t('taskforce.members.roleLabel')}</Label>
              <Select
                value={adding.role_in_project}
                onChange={(e) =>
                  setAdding({
                    ...adding,
                    role_in_project: e.target.value ? Number(e.target.value) : '',
                  })
                }
                disabled={busy}
              >
                <option value="">{t('taskforce.members.roleOptions.system')}</option>
                {roles.map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </Select>
            </div>
            <Button onClick={handleAdd} disabled={busy || !adding.user_id}>
              <UserPlus className="h-4 w-4" />
              {t('taskforce.members.addLabel')}
            </Button>
          </div>
        </div>
      )}

      {/* Members list */}
      <div className="rounded-lg border bg-card">
        <div className="border-b px-4 py-3">
          <h3 className="text-sm font-medium">
            {t('taskforce.members.manageTitle')}
            <span className="ml-2 text-xs text-muted-foreground">
              ({members.length})
            </span>
          </h3>
        </div>
        {members.length === 0 ? (
          <div className="p-8 text-center text-sm text-muted-foreground">
            {t('taskforce.members.noMembers')}
          </div>
        ) : (
          <ul className="divide-y">
            {members.map((m) => (
              <li
                key={m.id}
                className="flex items-center justify-between px-4 py-3 text-sm"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-xs font-medium uppercase">
                    {(m.user_name ?? '?').slice(0, 2)}
                  </div>
                  <div className="flex flex-col leading-tight">
                    <span className="font-mono">{m.user_name}</span>
                    {m.joined_at && (
                      <span className="text-xs text-muted-foreground">
                        {t('taskforce.members.addedAt')}:{' '}
                        {new Date(m.joined_at).toLocaleString()}
                      </span>
                    )}
                  </div>
                  <Badge
                    variant={m.role_in_project !== null ? 'default' : 'outline'}
                    className="ml-2"
                  >
                    {roleLabel(m)}
                  </Badge>
                  {!m.is_active && (
                    <Badge variant="secondary">{t('common.inactive')}</Badge>
                  )}
                </div>
                {canEdit && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleRemove(m)}
                    title={t('taskforce.members.removeLabel')}
                    disabled={busy}
                  >
                    <UserMinus className="h-4 w-4" />
                  </Button>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
