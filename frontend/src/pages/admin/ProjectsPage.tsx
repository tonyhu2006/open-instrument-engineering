import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Edit, Trash2, Database, Network } from 'lucide-react'
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
import { Select } from '@/components/ui/select'
import { RoleGuard } from '@/components/auth'
import {
  projectTenantApi,
  organizationCrudApi,
  type ProjectTenant,
  type Organization,
} from '@/lib/api'
import { AdminTable, type AdminColumn } from './components/AdminTable'
import { AdminPageHeader } from './components/AdminPageHeader'
import { usePermissions } from '@/hooks/usePermissions'

type ProjectStatus = ProjectTenant['status']

const STATUS_KEYS: ProjectStatus[] = ['ACTIVE', 'ON_HOLD', 'COMPLETED', 'CANCELLED']

const STATUS_VARIANTS: Record<ProjectStatus, 'default' | 'secondary' | 'outline' | 'destructive'> = {
  ACTIVE: 'default',
  ON_HOLD: 'secondary',
  COMPLETED: 'outline',
  CANCELLED: 'destructive',
}

export function ProjectsPage() {
  return (
    <RoleGuard require="canManageProjects">
      <ProjectsPageInner />
    </RoleGuard>
  )
}

function ProjectsPageInner() {
  const { t } = useTranslation()
  const perms = usePermissions()
  const navigate = useNavigate()
  const [data, setData] = useState<ProjectTenant[]>([])
  const [orgs, setOrgs] = useState<Organization[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')
  const [editing, setEditing] = useState<Partial<ProjectTenant> | null>(null)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const [projects, orgList] = await Promise.all([
        projectTenantApi.list(),
        organizationCrudApi.list().catch(() => [] as Organization[]),
      ])
      setData(projects)
      setOrgs(orgList)
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
      (p) =>
        p.project_no.toLowerCase().includes(q) ||
        p.name.toLowerCase().includes(q) ||
        (p.organization_name?.toLowerCase().includes(q) ?? false),
    )
  }, [data, search])

  const handleSave = async () => {
    if (!editing) return
    if (!editing.project_no || !editing.name || !editing.organization_id) {
      alert(t('projects.validation.requiredFields'))
      return
    }
    setSaving(true)
    try {
      if (editing.id) {
        // Schema/project_no immutable post-creation
        const payload: Partial<ProjectTenant> = {
          name: editing.name,
          description: editing.description,
          status: editing.status,
          start_date: editing.start_date,
          end_date: editing.end_date,
          hierarchy_config: editing.hierarchy_config,
        }
        await projectTenantApi.update(editing.id, payload)
      } else {
        await projectTenantApi.create(editing)
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

  const handleDelete = async (project: ProjectTenant) => {
    if (
      !confirm(
        t('projects.deleteConfirm', {
          projectNo: project.project_no,
          name: project.name,
          schema: project.schema_name,
        }),
      )
    )
      return
    try {
      await projectTenantApi.delete(project.id)
      await load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: unknown } }
      alert(`${t('common.deleteFailed')}: ${JSON.stringify(err.response?.data ?? e)}`)
    }
  }

  const columns: AdminColumn<ProjectTenant>[] = [
    {
      key: 'project_no',
      header: t('projects.columns.projectNo'),
      width: '160px',
      render: (r) => <span className="font-mono font-medium">{r.project_no}</span>,
    },
    { key: 'name', header: t('projects.columns.name') },
    {
      key: 'organization_name',
      header: t('projects.columns.organization'),
      render: (r) => r.organization_name ?? <span className="text-muted-foreground">—</span>,
    },
    {
      key: 'schema_name',
      header: t('projects.columns.schema'),
      width: '160px',
      render: (r) => (
        <span className="inline-flex items-center gap-1 font-mono text-xs text-muted-foreground">
          <Database className="h-3 w-3" />
          {r.schema_name}
        </span>
      ),
    },
    {
      key: 'status',
      header: t('projects.columns.status'),
      width: '100px',
      render: (r) => (
        <Badge variant={STATUS_VARIANTS[r.status]}>{t(`projects.status.${r.status}`)}</Badge>
      ),
    },
    {
      key: 'start_date',
      header: t('projects.columns.dateRange'),
      width: '180px',
      render: (r) => (
        <span className="text-xs text-muted-foreground">
          {r.start_date ?? '—'} → {r.end_date ?? '—'}
        </span>
      ),
    },
  ]

  return (
    <div>
      <AdminPageHeader
        title={t('projects.title')}
        description={t('projects.description')}
        searchValue={search}
        onSearchChange={setSearch}
        searchPlaceholder={t('projects.searchPlaceholder')}
        onRefresh={load}
        onCreate={
          perms.canManageProjects
            ? () =>
                setEditing({
                  project_no: '',
                  name: '',
                  description: '',
                  status: 'ACTIVE',
                  organization_id: orgs[0]?.id,
                  hierarchy_config: {},
                })
            : undefined
        }
        createLabel={t('projects.createLabel')}
      />

      <AdminTable
        storageKey="admin.projects"
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
              onClick={() => navigate(`/admin/projects/${r.id}/hierarchy`)}
              title={t('projects.openHierarchyTitle')}
            >
              <Network className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setEditing(r)}
              title={t('common.edit')}
            >
              <Edit className="h-4 w-4" />
            </Button>
            {perms.isAdmin && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => handleDelete(r)}
                title={t('projects.deleteTitleAdmin')}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </>
        )}
      />

      <Dialog open={!!editing} onOpenChange={(o) => !o && setEditing(null)}>
        {editing && (
          <>
            <DialogHeader>
              <DialogTitle>
                {editing.id ? t('projects.editTitle') : t('projects.createTitle')}
              </DialogTitle>
              <DialogDescription>
                {editing.id ? t('projects.editDescription') : t('projects.createDescription')}
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label htmlFor="prj-no">
                    {t('projects.fields.projectNo')} {t('common.required')}
                  </Label>
                  <Input
                    id="prj-no"
                    value={editing.project_no ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, project_no: e.target.value.toUpperCase() })
                    }
                    placeholder={t('projects.placeholder.projectNo')}
                    disabled={!!editing.id}
                    className="font-mono"
                  />
                  {!editing.id && (
                    <p className="text-xs text-muted-foreground">
                      {t('projects.schemaHint')}
                    </p>
                  )}
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor="prj-status">
                    {t('projects.fields.status')} {t('common.required')}
                  </Label>
                  <Select
                    id="prj-status"
                    value={editing.status ?? 'ACTIVE'}
                    onChange={(e) =>
                      setEditing({ ...editing, status: e.target.value as ProjectStatus })
                    }
                  >
                    {STATUS_KEYS.map((s) => (
                      <option key={s} value={s}>
                        {t(`projects.status.${s}`)}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>

              <div className="grid gap-1.5">
                <Label htmlFor="prj-name">
                  {t('projects.fields.name')} {t('common.required')}
                </Label>
                <Input
                  id="prj-name"
                  value={editing.name ?? ''}
                  onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                  placeholder={t('projects.placeholder.name')}
                />
              </div>

              <div className="grid gap-1.5">
                <Label htmlFor="prj-org">
                  {t('projects.fields.organization')} {t('common.required')}
                </Label>
                <Select
                  id="prj-org"
                  value={editing.organization_id ? String(editing.organization_id) : ''}
                  onChange={(e) =>
                    setEditing({
                      ...editing,
                      organization_id: e.target.value ? Number(e.target.value) : undefined,
                    })
                  }
                  disabled={!!editing.id}
                >
                  <option value="" disabled>
                    {t('projects.selectOrgPlaceholder')}
                  </option>
                  {orgs.map((o) => (
                    <option key={o.id} value={String(o.id)}>
                      {o.code} — {o.name}
                    </option>
                  ))}
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-1.5">
                  <Label htmlFor="prj-start">{t('projects.fields.startDate')}</Label>
                  <Input
                    id="prj-start"
                    type="date"
                    value={editing.start_date ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, start_date: e.target.value || null })
                    }
                  />
                </div>
                <div className="grid gap-1.5">
                  <Label htmlFor="prj-end">{t('projects.fields.endDate')}</Label>
                  <Input
                    id="prj-end"
                    type="date"
                    value={editing.end_date ?? ''}
                    onChange={(e) =>
                      setEditing({ ...editing, end_date: e.target.value || null })
                    }
                  />
                </div>
              </div>

              <div className="grid gap-1.5">
                <Label htmlFor="prj-desc">{t('projects.fields.description')}</Label>
                <Textarea
                  id="prj-desc"
                  rows={3}
                  value={editing.description ?? ''}
                  onChange={(e) => setEditing({ ...editing, description: e.target.value })}
                />
              </div>

              {editing.id && (
                <div className="rounded-md border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
                  <div>
                    <span className="font-medium">{t('projects.fields.schemaName')}:</span>{' '}
                    <span className="font-mono">{editing.schema_name}</span>
                  </div>
                  <div className="mt-1">
                    <span className="font-medium">{t('projects.fields.createdAt')}:</span>{' '}
                    {editing.created_at}
                  </div>
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
                  !editing.project_no ||
                  !editing.name ||
                  !editing.organization_id
                }
              >
                {saving
                  ? t('common.saving')
                  : editing.id
                    ? t('common.save')
                    : t('projects.submitCreate')}
              </Button>
            </DialogFooter>
          </>
        )}
      </Dialog>
    </div>
  )
}
