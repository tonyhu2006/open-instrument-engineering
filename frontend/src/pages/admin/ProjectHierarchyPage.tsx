import { useEffect, useMemo, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import type { TFunction } from 'i18next'
import {
  Building2,
  MapPin,
  Factory,
  Layers,
  Boxes,
  Plus,
  Edit,
  Trash2,
  ChevronRight,
  ChevronDown,
  ArrowLeft,
  Loader2,
  AlertCircle,
  Database,
} from 'lucide-react'
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
import {
  projectTenantApi,
  clientApi,
  siteApi,
  plantApi,
  plantHierarchyApi,
  setCurrentProject,
  type ProjectTenant,
  type Client,
  type Site,
  type Plant,
  type PlantHierarchy,
} from '@/lib/api'
import { cn } from '@/lib/utils'

type NodeType = 'client' | 'site' | 'plant' | 'area' | 'unit'

interface EditingState {
  type: NodeType
  data: Partial<Client & Site & Plant & PlantHierarchy>
  parentId?: number // client id (for site) / site id (for plant) / hierarchy parent id (for area/unit)
  // For area: the matching Plant model code, used to lazily create the PLANT root if missing
  plantCodeForRoot?: string
  plantNameForRoot?: string
}

export function ProjectHierarchyPage() {
  return (
    <RoleGuard require="canManageProjects">
      <ProjectHierarchyInner />
    </RoleGuard>
  )
}

function ProjectHierarchyInner() {
  const { t } = useTranslation()
  const { id } = useParams<{ id: string }>()
  const projectId = Number(id)

  const [project, setProject] = useState<ProjectTenant | null>(null)
  const [clients, setClients] = useState<Client[]>([])
  const [sites, setSites] = useState<Site[]>([])
  const [plants, setPlants] = useState<Plant[]>([])
  const [hierarchyNodes, setHierarchyNodes] = useState<PlantHierarchy[]>([])
  const [expanded, setExpanded] = useState<Set<string>>(new Set())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [editing, setEditing] = useState<EditingState | null>(null)
  const [saving, setSaving] = useState(false)

  // Persist original project so we can restore on unmount
  useEffect(() => {
    if (!projectId) return
    const previous = localStorage.getItem('current_project_id')
    setCurrentProject(projectId)
    return () => {
      // Restore previously active tenant on leave
      const prev = previous ? Number(previous) : null
      setCurrentProject(prev)
    }
  }, [projectId])

  const load = async () => {
    if (!projectId) return
    setLoading(true)
    setError(null)
    try {
      // Ensure header is set before fetching tenant data
      setCurrentProject(projectId)
      const [proj, cl, st, pl, hn] = await Promise.all([
        projectTenantApi.get(projectId),
        clientApi.list(),
        siteApi.list(),
        plantApi.list(),
        plantHierarchyApi.list(),
      ])
      setProject(proj)
      setClients(cl)
      setSites(st)
      setPlants(pl)
      setHierarchyNodes(hn)
      // Auto-expand all clients/sites/plants on first load
      if (expanded.size === 0) {
        setExpanded(
          new Set([
            ...cl.map((c) => `client-${c.id}`),
            ...st.map((s) => `site-${s.id}`),
            ...pl.map((p) => `plant-${p.id}`),
            ...hn
              .filter((n) => n.node_type === 'AREA')
              .map((a) => `area-${a.id}`),
          ]),
        )
      }
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

  const sitesByClient = useMemo(() => {
    const map = new Map<number, Site[]>()
    for (const s of sites) {
      const list = map.get(s.client) ?? []
      list.push(s)
      map.set(s.client, list)
    }
    return map
  }, [sites])

  const plantsBySite = useMemo(() => {
    const map = new Map<number, Plant[]>()
    for (const p of plants) {
      const list = map.get(p.site) ?? []
      list.push(p)
      map.set(p.site, list)
    }
    return map
  }, [plants])

  // PLANT root nodes (parent=null, node_type=PLANT) indexed by code — used to
  // bridge Plant model rows to their MPTT subtree via code matching.
  const plantRootByCode = useMemo(() => {
    const map = new Map<string, PlantHierarchy>()
    for (const n of hierarchyNodes) {
      if (n.node_type === 'PLANT' && n.parent === null) {
        map.set(n.code, n)
      }
    }
    return map
  }, [hierarchyNodes])

  // AREA nodes grouped by parent (PLANT root id)
  const areasByPlantRoot = useMemo(() => {
    const map = new Map<number, PlantHierarchy[]>()
    for (const n of hierarchyNodes) {
      if (n.node_type === 'AREA' && n.parent !== null) {
        const list = map.get(n.parent) ?? []
        list.push(n)
        map.set(n.parent, list)
      }
    }
    return map
  }, [hierarchyNodes])

  // UNIT nodes grouped by parent (AREA id)
  const unitsByArea = useMemo(() => {
    const map = new Map<number, PlantHierarchy[]>()
    for (const n of hierarchyNodes) {
      if (n.node_type === 'UNIT' && n.parent !== null) {
        const list = map.get(n.parent) ?? []
        list.push(n)
        map.set(n.parent, list)
      }
    }
    return map
  }, [hierarchyNodes])

  const toggle = (key: string) => {
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(key)) next.delete(key)
      else next.add(key)
      return next
    })
  }

  const handleSave = async () => {
    if (!editing) return
    setSaving(true)
    try {
      const d = editing.data
      if (editing.type === 'client') {
        if (d.id) await clientApi.update(d.id, d)
        else await clientApi.create(d)
      } else if (editing.type === 'site') {
        const payload: Partial<Site> = { ...d, client: d.client ?? editing.parentId }
        if (d.id) await siteApi.update(d.id, payload)
        else await siteApi.create(payload)
      } else if (editing.type === 'plant') {
        const payload: Partial<Plant> = { ...d, site: d.site ?? editing.parentId }
        if (d.id) await plantApi.update(d.id, payload)
        else await plantApi.create(payload)
      } else if (editing.type === 'area') {
        if (d.id) {
          await plantHierarchyApi.update(d.id, {
            code: d.code,
            name: d.name,
            description: d.description,
            is_active: d.is_active,
          })
        } else {
          // Lazy-create the PLANT root when adding the first AREA under a Plant
          let parentId = editing.parentId
          if (!parentId && editing.plantCodeForRoot) {
            const root = await plantHierarchyApi.create({
              code: editing.plantCodeForRoot,
              name: editing.plantNameForRoot ?? editing.plantCodeForRoot,
              node_type: 'PLANT',
              parent: null,
              is_active: true,
            })
            parentId = root.id
          }
          await plantHierarchyApi.create({
            code: d.code,
            name: d.name,
            description: d.description,
            node_type: 'AREA',
            parent: parentId ?? null,
            is_active: d.is_active ?? true,
          })
        }
      } else if (editing.type === 'unit') {
        if (d.id) {
          await plantHierarchyApi.update(d.id, {
            code: d.code,
            name: d.name,
            description: d.description,
            is_active: d.is_active,
          })
        } else {
          await plantHierarchyApi.create({
            code: d.code,
            name: d.name,
            description: d.description,
            node_type: 'UNIT',
            parent: editing.parentId ?? null,
            is_active: d.is_active ?? true,
          })
        }
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

  const handleDelete = async (
    type: NodeType,
    node: Client | Site | Plant | PlantHierarchy,
  ) => {
    const label = t(`hierarchy.labels.${type}`)
    const cascadeMsg = t(`hierarchy.cascade.${type}`)
    if (
      !confirm(
        t('hierarchy.deleteConfirm', {
          label,
          code: (node as Client).code,
          name: (node as Client).name,
          cascade: cascadeMsg,
        }),
      )
    )
      return
    try {
      if (type === 'client') await clientApi.delete(node.id)
      else if (type === 'site') await siteApi.delete(node.id)
      else if (type === 'plant') await plantApi.delete(node.id)
      else await plantHierarchyApi.delete(node.id) // area / unit
      await load()
    } catch (e: unknown) {
      const err = e as { response?: { data?: unknown } }
      alert(`${t('common.deleteFailed')}: ${JSON.stringify(err.response?.data ?? e)}`)
    }
  }

  if (loading) {
    return (
      <div className="flex h-60 items-center justify-center text-muted-foreground">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        {t('hierarchy.loading')}
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

  if (!project) {
    return (
      <div className="flex h-60 items-center justify-center text-muted-foreground">
        {t('hierarchy.projectNotFound')}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Breadcrumb / back */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <Link
            to="/admin/projects"
            className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            {t('hierarchy.back')}
          </Link>
        </div>
        <div className="flex items-center gap-2 rounded-full border bg-background px-3 py-1.5 text-xs">
          <Database className="h-3.5 w-3.5" />
          <span className="font-mono">{project.schema_name}</span>
        </div>
      </div>

      {/* Project header */}
      <div className="rounded-lg border bg-card p-4">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Badge variant="default" className="font-mono">
                {project.project_no}
              </Badge>
              <h2 className="text-lg font-semibold">{project.name}</h2>
            </div>
            {project.description && (
              <p className="mt-1 text-sm text-muted-foreground">{project.description}</p>
            )}
            <div className="mt-2 flex flex-wrap gap-4 text-xs text-muted-foreground">
              <span>{t('hierarchy.stat.organization')}: {project.organization_name ?? '—'}</span>
              <span>{t('hierarchy.stat.clients')}: {clients.length}</span>
              <span>{t('hierarchy.stat.sites')}: {sites.length}</span>
              <span>{t('hierarchy.stat.plants')}: {plants.length}</span>
              <span>{t('hierarchy.stat.areas')}: {hierarchyNodes.filter((n) => n.node_type === 'AREA').length}</span>
              <span>{t('hierarchy.stat.units')}: {hierarchyNodes.filter((n) => n.node_type === 'UNIT').length}</span>
            </div>
          </div>
          {clients.length === 0 ? (
            <Button
              size="sm"
              onClick={() =>
                setEditing({
                  type: 'client',
                  data: { code: '', name: '', contact_person: '', contact_email: '' },
                })
              }
            >
              <Plus className="h-4 w-4" />
              {t('hierarchy.client.create')}
            </Button>
          ) : (
            <Button
              size="sm"
              variant="outline"
              onClick={() => setEditing({ type: 'client', data: clients[0] })}
            >
              <Edit className="h-4 w-4" />
              {t('hierarchy.client.edit')}
            </Button>
          )}
        </div>
      </div>

      {/* Hierarchy tree */}
      <div className="rounded-lg border bg-card">
        {clients.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 p-8 text-sm text-muted-foreground">
            <Building2 className="h-8 w-8 opacity-40" />
            <span>{t('hierarchy.noClientPlaceholder')}</span>
          </div>
        ) : (
          <div className="divide-y">
            {clients.map((client) => {
              const clientKey = `client-${client.id}`
              const isClientExpanded = expanded.has(clientKey)
              const clientSites = sitesByClient.get(client.id) ?? []
              return (
                <div key={client.id}>
                  {/* Client row */}
                  <TreeRow
                    indent={0}
                    icon={Building2}
                    iconColor="text-blue-500"
                    code={client.code}
                    name={client.name}
                    meta={
                      clientSites.length > 0
                        ? t('hierarchy.meta.siteCount', { count: clientSites.length })
                        : t('hierarchy.meta.noSites')
                    }
                    expanded={isClientExpanded}
                    hasChildren={clientSites.length > 0}
                    onToggle={() => toggle(clientKey)}
                    actions={
                      <>
                        <IconBtn
                          title={t('hierarchy.client.newSite')}
                          onClick={() =>
                            setEditing({
                              type: 'site',
                              parentId: client.id,
                              data: {
                                client: client.id,
                                code: '',
                                name: '',
                                location: '',
                                timezone: 'Asia/Shanghai',
                              },
                            })
                          }
                        >
                          <Plus className="h-3.5 w-3.5" />
                        </IconBtn>
                        <IconBtn
                          title={t('hierarchy.client.edit')}
                          onClick={() => setEditing({ type: 'client', data: client })}
                        >
                          <Edit className="h-3.5 w-3.5" />
                        </IconBtn>
                        <IconBtn
                          title={t('hierarchy.client.delete')}
                          onClick={() => handleDelete('client', client)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </IconBtn>
                      </>
                    }
                  />

                  {/* Sites */}
                  {isClientExpanded &&
                    clientSites.map((site) => {
                      const siteKey = `site-${site.id}`
                      const isSiteExpanded = expanded.has(siteKey)
                      const sitePlants = plantsBySite.get(site.id) ?? []
                      return (
                        <div key={site.id}>
                          <TreeRow
                            indent={1}
                            icon={MapPin}
                            iconColor="text-emerald-500"
                            code={site.code}
                            name={site.name}
                            meta={site.location || site.timezone}
                            expanded={isSiteExpanded}
                            hasChildren={sitePlants.length > 0}
                            onToggle={() => toggle(siteKey)}
                            actions={
                              <>
                                <IconBtn
                                  title={t('hierarchy.site.newPlant')}
                                  onClick={() =>
                                    setEditing({
                                      type: 'plant',
                                      parentId: site.id,
                                      data: {
                                        site: site.id,
                                        code: '',
                                        name: '',
                                        description: '',
                                        capacity: '',
                                        is_active: true,
                                      },
                                    })
                                  }
                                >
                                  <Plus className="h-3.5 w-3.5" />
                                </IconBtn>
                                <IconBtn
                                  title={t('hierarchy.site.edit')}
                                  onClick={() =>
                                    setEditing({
                                      type: 'site',
                                      parentId: site.client,
                                      data: site,
                                    })
                                  }
                                >
                                  <Edit className="h-3.5 w-3.5" />
                                </IconBtn>
                                <IconBtn
                                  title={t('hierarchy.site.delete')}
                                  onClick={() => handleDelete('site', site)}
                                >
                                  <Trash2 className="h-3.5 w-3.5" />
                                </IconBtn>
                              </>
                            }
                          />

                          {/* Plants */}
                          {isSiteExpanded &&
                            sitePlants.map((plant) => {
                              const plantKey = `plant-${plant.id}`
                              const isPlantExpanded = expanded.has(plantKey)
                              const plantRoot = plantRootByCode.get(plant.code)
                              const areas = plantRoot
                                ? areasByPlantRoot.get(plantRoot.id) ?? []
                                : []
                              return (
                                <div key={plant.id}>
                                  <TreeRow
                                    indent={2}
                                    icon={Factory}
                                    iconColor="text-orange-500"
                                    code={plant.code}
                                    name={plant.name}
                                    meta={
                                      [
                                        plant.capacity,
                                        areas.length > 0
                                          ? t('hierarchy.meta.areaCount', { count: areas.length })
                                          : null,
                                        plant.is_active ? null : t('hierarchy.meta.deactivated'),
                                      ]
                                        .filter(Boolean)
                                        .join(' · ') || undefined
                                    }
                                    expanded={isPlantExpanded}
                                    hasChildren={areas.length > 0}
                                    onToggle={() => toggle(plantKey)}
                                    actions={
                                      <>
                                        <IconBtn
                                          title={t('hierarchy.plant.newArea')}
                                          onClick={() =>
                                            setEditing({
                                              type: 'area',
                                              parentId: plantRoot?.id,
                                              plantCodeForRoot: plant.code,
                                              plantNameForRoot: plant.name,
                                              data: {
                                                code: '',
                                                name: '',
                                                description: '',
                                                is_active: true,
                                              },
                                            })
                                          }
                                        >
                                          <Plus className="h-3.5 w-3.5" />
                                        </IconBtn>
                                        <IconBtn
                                          title={t('hierarchy.plant.edit')}
                                          onClick={() =>
                                            setEditing({
                                              type: 'plant',
                                              parentId: plant.site,
                                              data: plant,
                                            })
                                          }
                                        >
                                          <Edit className="h-3.5 w-3.5" />
                                        </IconBtn>
                                        <IconBtn
                                          title={t('hierarchy.plant.delete')}
                                          onClick={() => handleDelete('plant', plant)}
                                        >
                                          <Trash2 className="h-3.5 w-3.5" />
                                        </IconBtn>
                                      </>
                                    }
                                  />

                                  {/* Areas */}
                                  {isPlantExpanded &&
                                    areas.map((area) => {
                                      const areaKey = `area-${area.id}`
                                      const isAreaExpanded = expanded.has(areaKey)
                                      const units = unitsByArea.get(area.id) ?? []
                                      return (
                                        <div key={area.id}>
                                          <TreeRow
                                            indent={3}
                                            icon={Layers}
                                            iconColor="text-purple-500"
                                            code={area.code}
                                            name={area.name}
                                            meta={
                                              units.length > 0
                                                ? t('hierarchy.meta.unitCount', { count: units.length })
                                                : t('hierarchy.meta.noUnits')
                                            }
                                            expanded={isAreaExpanded}
                                            hasChildren={units.length > 0}
                                            onToggle={() => toggle(areaKey)}
                                            actions={
                                              <>
                                                <IconBtn
                                                  title={t('hierarchy.area.newUnit')}
                                                  onClick={() =>
                                                    setEditing({
                                                      type: 'unit',
                                                      parentId: area.id,
                                                      data: {
                                                        code: '',
                                                        name: '',
                                                        description: '',
                                                        is_active: true,
                                                      },
                                                    })
                                                  }
                                                >
                                                  <Plus className="h-3.5 w-3.5" />
                                                </IconBtn>
                                                <IconBtn
                                                  title={t('hierarchy.area.edit')}
                                                  onClick={() =>
                                                    setEditing({
                                                      type: 'area',
                                                      parentId: area.parent ?? undefined,
                                                      data: area,
                                                    })
                                                  }
                                                >
                                                  <Edit className="h-3.5 w-3.5" />
                                                </IconBtn>
                                                <IconBtn
                                                  title={t('hierarchy.area.delete')}
                                                  onClick={() => handleDelete('area', area)}
                                                >
                                                  <Trash2 className="h-3.5 w-3.5" />
                                                </IconBtn>
                                              </>
                                            }
                                          />

                                          {/* Units */}
                                          {isAreaExpanded &&
                                            units.map((unit) => (
                                              <TreeRow
                                                key={unit.id}
                                                indent={4}
                                                icon={Boxes}
                                                iconColor="text-pink-500"
                                                code={unit.code}
                                                name={unit.name}
                                                meta={
                                                  unit.is_active ? undefined : t('hierarchy.meta.deactivated')
                                                }
                                                actions={
                                                  <>
                                                    <IconBtn
                                                      title={t('hierarchy.unit.edit')}
                                                      onClick={() =>
                                                        setEditing({
                                                          type: 'unit',
                                                          parentId: unit.parent ?? undefined,
                                                          data: unit,
                                                        })
                                                      }
                                                    >
                                                      <Edit className="h-3.5 w-3.5" />
                                                    </IconBtn>
                                                    <IconBtn
                                                      title={t('hierarchy.unit.delete')}
                                                      onClick={() =>
                                                        handleDelete('unit', unit)
                                                      }
                                                    >
                                                      <Trash2 className="h-3.5 w-3.5" />
                                                    </IconBtn>
                                                  </>
                                                }
                                              />
                                            ))}
                                        </div>
                                      )
                                    })}
                                </div>
                              )
                            })}
                        </div>
                      )
                    })}
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* Edit dialog */}
      <Dialog open={!!editing} onOpenChange={(o) => !o && setEditing(null)}>
        {editing && (
          <EditDialogContent
            editing={editing}
            onChange={(data) => setEditing({ ...editing, data })}
            onCancel={() => setEditing(null)}
            onSave={handleSave}
            saving={saving}
            t={t}
          />
        )}
      </Dialog>
    </div>
  )
}

// ============================================================================
// Subcomponents
// ============================================================================

interface TreeRowProps {
  indent: number
  icon: React.ComponentType<{ className?: string }>
  iconColor: string
  code: string
  name: string
  meta?: string
  expanded?: boolean
  hasChildren?: boolean
  onToggle?: () => void
  actions?: React.ReactNode
}

function TreeRow({
  indent,
  icon: Icon,
  iconColor,
  code,
  name,
  meta,
  expanded,
  hasChildren,
  onToggle,
  actions,
}: TreeRowProps) {
  return (
    <div
      className="group flex items-center gap-2 px-3 py-2 hover:bg-muted/30"
      style={{ paddingLeft: `${12 + indent * 24}px` }}
    >
      <button
        type="button"
        onClick={onToggle}
        disabled={!onToggle}
        className={cn(
          'flex h-5 w-5 flex-none items-center justify-center rounded hover:bg-muted',
          !onToggle && 'cursor-default opacity-0',
          !hasChildren && 'invisible',
        )}
      >
        {expanded ? (
          <ChevronDown className="h-3.5 w-3.5" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5" />
        )}
      </button>
      <Icon className={cn('h-4 w-4 flex-none', iconColor)} />
      <div className="flex min-w-0 flex-1 items-baseline gap-2">
        <span className="font-mono text-sm font-medium">{code}</span>
        <span className="truncate text-sm">{name}</span>
        {meta && (
          <span className="truncate text-xs text-muted-foreground">— {meta}</span>
        )}
      </div>
      <div className="flex flex-none items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100">
        {actions}
      </div>
    </div>
  )
}

function IconBtn({
  title,
  onClick,
  children,
}: {
  title: string
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className="h-7 w-7"
      title={title}
      onClick={onClick}
    >
      {children}
    </Button>
  )
}

interface EditDialogContentProps {
  editing: EditingState
  onChange: (data: EditingState['data']) => void
  onCancel: () => void
  onSave: () => void
  saving: boolean
  t: TFunction
}

function EditDialogContent({
  editing,
  onChange,
  onCancel,
  onSave,
  saving,
  t,
}: EditDialogContentProps) {
  const d = editing.data
  const isNew = !d.id
  const ns = editing.type // 'client' | 'site' | 'plant' | 'area' | 'unit'
  const dialogTitle = isNew
    ? t(`hierarchy.${ns}.createTitle`)
    : t(`hierarchy.${ns}.editTitle`)
  const dialogDescription = t(`hierarchy.${ns}.description`)

  return (
    <>
      <DialogHeader>
        <DialogTitle>{dialogTitle}</DialogTitle>
        <DialogDescription>{dialogDescription}</DialogDescription>
      </DialogHeader>
      <div className="grid gap-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="grid gap-1.5">
            <Label htmlFor="node-code">
              {t('common.code')} {t('common.required')}
            </Label>
            <Input
              id="node-code"
              className="font-mono"
              value={d.code ?? ''}
              onChange={(e) => onChange({ ...d, code: e.target.value.toUpperCase() })}
              placeholder={t(`hierarchy.${ns}.placeholder.code`)}
            />
          </div>
          <div className="grid gap-1.5">
            <Label htmlFor="node-name">
              {t('common.name')} {t('common.required')}
            </Label>
            <Input
              id="node-name"
              value={d.name ?? ''}
              onChange={(e) => onChange({ ...d, name: e.target.value })}
            />
          </div>
        </div>

        {editing.type === 'client' && (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-1.5">
                <Label htmlFor="c-contact">{t('hierarchy.client.fields.contactPerson')}</Label>
                <Input
                  id="c-contact"
                  value={d.contact_person ?? ''}
                  onChange={(e) => onChange({ ...d, contact_person: e.target.value })}
                />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="c-email">{t('hierarchy.client.fields.contactEmail')}</Label>
                <Input
                  id="c-email"
                  type="email"
                  value={d.contact_email ?? ''}
                  onChange={(e) => onChange({ ...d, contact_email: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="c-phone">{t('hierarchy.client.fields.contactPhone')}</Label>
              <Input
                id="c-phone"
                value={d.contact_phone ?? ''}
                onChange={(e) => onChange({ ...d, contact_phone: e.target.value })}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="c-addr">{t('hierarchy.client.fields.address')}</Label>
              <Textarea
                id="c-addr"
                rows={2}
                value={d.address ?? ''}
                onChange={(e) => onChange({ ...d, address: e.target.value })}
              />
            </div>
          </>
        )}

        {editing.type === 'site' && (
          <>
            <div className="grid gap-1.5">
              <Label htmlFor="s-loc">{t('hierarchy.site.fields.location')}</Label>
              <Input
                id="s-loc"
                value={d.location ?? ''}
                onChange={(e) => onChange({ ...d, location: e.target.value })}
                placeholder={t('hierarchy.site.placeholder.location')}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-1.5">
                <Label htmlFor="s-tz">{t('hierarchy.site.fields.timezone')}</Label>
                <Input
                  id="s-tz"
                  value={d.timezone ?? 'Asia/Shanghai'}
                  onChange={(e) => onChange({ ...d, timezone: e.target.value })}
                />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="s-addr">{t('hierarchy.site.fields.address')}</Label>
              <Textarea
                id="s-addr"
                rows={2}
                value={d.address ?? ''}
                onChange={(e) => onChange({ ...d, address: e.target.value })}
              />
            </div>
          </>
        )}

        {editing.type === 'plant' && (
          <>
            <div className="grid gap-1.5">
              <Label htmlFor="p-capacity">{t('hierarchy.plant.fields.capacity')}</Label>
              <Input
                id="p-capacity"
                value={d.capacity ?? ''}
                onChange={(e) => onChange({ ...d, capacity: e.target.value })}
                placeholder={t('hierarchy.plant.placeholder.capacity')}
              />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="p-desc">{t('hierarchy.plant.fields.description')}</Label>
              <Textarea
                id="p-desc"
                rows={3}
                value={d.description ?? ''}
                onChange={(e) => onChange({ ...d, description: e.target.value })}
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={d.is_active ?? true}
                onChange={(e) => onChange({ ...d, is_active: e.target.checked })}
              />
              {t('hierarchy.checkbox.isActive')}
            </label>
          </>
        )}

        {(editing.type === 'area' || editing.type === 'unit') && (
          <>
            <div className="grid gap-1.5">
              <Label htmlFor="h-desc">{t('common.description')}</Label>
              <Textarea
                id="h-desc"
                rows={3}
                value={d.description ?? ''}
                onChange={(e) => onChange({ ...d, description: e.target.value })}
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={d.is_active ?? true}
                onChange={(e) => onChange({ ...d, is_active: e.target.checked })}
              />
              {t('hierarchy.checkbox.isActive')}
            </label>
            {isNew && !editing.parentId && editing.type === 'area' && editing.plantCodeForRoot && (
              <p className="rounded-md border bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
                {t('hierarchy.lazyPlantRoot', { code: editing.plantCodeForRoot })}
              </p>
            )}
          </>
        )}
      </div>
      <DialogFooter>
        <Button variant="outline" onClick={onCancel} disabled={saving}>
          {t('common.cancel')}
        </Button>
        <Button onClick={onSave} disabled={saving || !d.code || !d.name}>
          {saving ? t('common.saving') : t('common.save')}
        </Button>
      </DialogFooter>
    </>
  )
}
