import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Edit, Trash2, Users as UsersIcon } from 'lucide-react'
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
  apiError,
  apiErrorMessage,
  taskForceApi,
  userApi,
  projectTenantApi,
  type ProjectTaskForce,
  type ProjectTenant,
  type UserProfile,
} from '@/lib/api'
import { useHierarchy } from '@/components/hierarchy'
import { usePermissions } from '@/hooks/usePermissions'
import { useCurrentUser } from '@/contexts/CurrentUserContext'
import { AdminTable, type AdminColumn } from './components/AdminTable'
import { AdminPageHeader } from './components/AdminPageHeader'

export function TaskForcesPage() {
  return (
    <RoleGuard require="canManageTaskForces">
      <TaskForcesPageInner />
    </RoleGuard>
  )
}

function TaskForcesPageInner() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { selectedProject } = useHierarchy()
  const perms = usePermissions()
  const { user: currentUser } = useCurrentUser()
  const [data, setData] = useState<ProjectTaskForce[]>([])
  const [users, setUsers] = useState<UserProfile[]>([])
  const [projects, setProjects] = useState<ProjectTenant[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<Partial<ProjectTaskForce> | null>(null)
  const [saving, setSaving] = useState(false)

  const projectId = selectedProject?.id

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [tf, u, p] = await Promise.all([
        taskForceApi.list(),
        userApi.list().catch(() => [] as UserProfile[]),
        projectTenantApi.list().catch(() => [] as ProjectTenant[]),
      ])
      setData(tf)
      setUsers(u)
      setProjects(p)
    } catch (e) {
      setError(e instanceof Error ? e.message : t('common.loadFailed'))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId])

  const projectById = useMemo(() => {
    const m = new Map<number, ProjectTenant>()
    for (const p of projects) m.set(p.id, p)
    return m
  }, [projects])

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase()
    if (!q) return data
    return data.filter((tf) => {
      const proj = tf.project_id !== null ? projectById.get(tf.project_id) : undefined
      return (
        tf.code.toLowerCase().includes(q) ||
        tf.name.toLowerCase().includes(q) ||
        (proj?.project_no?.toLowerCase().includes(q) ?? false) ||
        (proj?.name?.toLowerCase().includes(q) ?? false)
      )
    })
  }, [data, search, projectById])

  // ADM-TF01: Administrators may create an empty group and assign the project
  // later; Project Engineers / Managers must start from an existing project.
  const projectRequired = !perms.isAdmin

  const handleSave = async () => {
    if (!editing) return
    if (projectRequired && !editing.project_id) {
      alert(t('taskforce.errors.selectProject'))
      return
    }
    setSaving(true)
    try {
      if (editing.id) {
        // Only administrators may relink the project or change the leader.
        const payload: Partial<ProjectTaskForce> = perms.isAdmin
          ? {
              code: editing.code,
              name: editing.name,
              description: editing.description,
              is_active: editing.is_active,
              project_id: editing.project_id ?? null,
              leader: editing.leader ?? null,
            }
          : {
              code: editing.code,
              name: editing.name,
              description: editing.description,
              is_active: editing.is_active,
            }
        await taskForceApi.update(editing.id, payload)
      } else {
        await taskForceApi.create({ ...editing, project_id: editing.project_id ?? null })
      }
      setEditing(null)
      await load()
    } catch (e: unknown) {
      const err = apiError(e)
      if (err?.code === 'ADM_TASK_FORCE_PROJECT_TAKEN') {
        const projName =
          projects.find((p) => p.id === editing.project_id)?.project_no ?? '—'
        alert(t('taskforce.errors.projectTaken', { project: projName }))
      } else {
        alert(`${t('common.saveFailed')}: ${apiErrorMessage(e)}`)
      }
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (tf: ProjectTaskForce) => {
    if (!confirm(t('taskforce.members.deleteConfirm', { name: tf.name }))) return
    try {
      await taskForceApi.delete(tf.id)
      await load()
    } catch (e: unknown) {
      alert(`${t('common.deleteFailed')}: ${apiErrorMessage(e)}`)
    }
  }

  const columns: AdminColumn<ProjectTaskForce>[] = [
    {
      key: 'project',
      header: t('taskforce.columns.project'),
      width: '260px',
      render: (r) => {
        if (r.project_id === null) {
          return (
            <span className="text-xs text-muted-foreground">{t('taskforce.unassigned')}</span>
          )
        }
        const proj = projectById.get(r.project_id)
        if (!proj) {
          return (
            <span className="text-xs text-muted-foreground">
              {t('taskforce.errors.unknownProject', { id: r.project_id })}
            </span>
          )
        }
        return (
          <div className="flex flex-col leading-tight">
            <span className="font-mono text-xs">{proj.project_no}</span>
            <span className="truncate text-xs text-muted-foreground">{proj.name}</span>
          </div>
        )
      },
    },
    {
      key: 'code',
      header: t('taskforce.columns.code'),
      width: '140px',
      render: (r) => <span className="font-mono">{r.code}</span>,
    },
    { key: 'name', header: t('taskforce.columns.name') },
    {
      key: 'leader',
      header: t('taskforce.columns.leader'),
      render: (r) =>
        r.leader_name ? (
          <span>
            {r.leader_name}
            {currentUser && r.created_by === currentUser.id && (
              <Badge variant="outline" className="ml-2 text-xs">
                {t('taskforce.createdByMe')}
              </Badge>
            )}
          </span>
        ) : (
          '—'
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
        title={t('taskforce.title')}
        description={
          perms.isAdmin ? t('taskforce.descriptionAdmin') : t('taskforce.descriptionPe')
        }
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder={t('taskforce.searchPlaceholder')}
        onRefresh={load}
        onCreate={
          perms.canManageTaskForces
            ? () =>
                setEditing({
                  project_id: projectId ?? null,
                  code: '',
                  name: '',
                  description: '',
                  is_active: true,
                })
            : undefined
        }
        createLabel={t('taskforce.createLabel')}
      />

      <AdminTable
        storageKey="admin.taskForces"
        data={filtered}
        columns={columns}
        loading={loading}
        error={error}
        rowKey={(r) => r.id}
        actions={(r) => {
          const canEdit = perms.canEditOwnTaskForce(r.created_by)
          return (
            <>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate(`/admin/task-forces/${r.id}/members`)}
                title={t('common.members')}
              >
                <UsersIcon className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setEditing(r)}
                title={canEdit ? t('common.edit') : t('common.noPermission')}
                disabled={!canEdit}
              >
                <Edit className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(r)}
                title={canEdit ? t('common.delete') : t('common.noPermission')}
                disabled={!canEdit}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </>
          )
        }}
      />

      {/* Edit dialog */}
      <Dialog open={!!editing} onOpenChange={(o) => !o && setEditing(null)}>
        {editing && (
          <>
            <DialogHeader>
              <DialogTitle>
                {editing.id ? t('taskforce.editTitle') : t('taskforce.createTitle')}
              </DialogTitle>
              <DialogDescription>
                {perms.isAdmin
                  ? t('taskforce.createDescAdmin')
                  : t('taskforce.createDescPe')}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4">
              <div className="grid grid-cols-2 gap-3">
                <div className="grid gap-1.5">
                  <Label>
                    {t('taskforce.fields.code')} {t('common.required')}
                  </Label>
                  <Input
                    value={editing.code ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, code: e.target.value.toUpperCase() })
                    }
                    placeholder="e.g. TF-001"
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label>
                    {t('taskforce.fields.name')} {t('common.required')}
                  </Label>
                  <Input
                    value={editing.name ?? ''}
                    onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid gap-1.5">
                <Label>
                  {t('taskforce.fields.project')} {projectRequired && t('common.required')}
                </Label>
                <Select
                  value={editing.project_id ? String(editing.project_id) : ''}
                  onChange={(e) =>
                    setEditing({
                      ...editing,
                      project_id: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                  disabled={!!editing.id && !perms.isAdmin}
                >
                  <option value="" disabled={projectRequired}>
                    {projectRequired
                      ? t('taskforce.selectProjectPlaceholder')
                      : t('taskforce.unassigned')}
                  </option>
                  {projects.map((p) => (
                    <option key={p.id} value={String(p.id)}>
                      {p.project_no} — {p.name}
                    </option>
                  ))}
                </Select>
                {editing.id && !perms.isAdmin && (
                  <p className="text-xs text-muted-foreground">
                    {t('taskforce.projectLockedHint')}
                  </p>
                )}
              </div>
              <div className="grid gap-1.5">
                <Label>{t('taskforce.fields.description')}</Label>
                <Textarea
                  value={editing.description ?? ''}
                  onChange={(e) => setEditing({ ...editing, description: e.target.value })}
                />
              </div>
              {perms.isAdmin && (
                <div className="grid gap-1.5">
                  <Label>{t('taskforce.fields.leader')}</Label>
                  <Select
                    value={editing.leader ?? ''}
                    onChange={(e) =>
                      setEditing({
                        ...editing,
                        leader: e.target.value ? Number(e.target.value) : null,
                      })
                    }
                  >
                    <option value="">{t('taskforce.noLeader')}</option>
                    {users.map((u) => (
                      <option key={u.id} value={u.id}>
                        {u.username}
                      </option>
                    ))}
                  </Select>
                </div>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setEditing(null)} disabled={saving}>
                {t('common.cancel')}
              </Button>
              <Button
                onClick={handleSave}
                disabled={
                  saving ||
                  !editing.code ||
                  !editing.name ||
                  (projectRequired && !editing.project_id)
                }
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
