import axios from 'axios'
import i18n from '@/i18n'

/**
 * API client — SPECIFICATION §4.2.1: every endpoint lives under `/api/v1`
 * (decisions D1/D2). Tenant-scoped requests carry `X-Project-ID` (ADM-T01).
 */
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Current project ID for tenant switching
let currentProjectId: number | null = null

export const setCurrentProject = (projectId: number | null) => {
  currentProjectId = projectId
  if (projectId) {
    localStorage.setItem('current_project_id', String(projectId))
  } else {
    localStorage.removeItem('current_project_id')
  }
}

export const getCurrentProject = (): number | null => {
  if (currentProjectId) return currentProjectId
  const stored = localStorage.getItem('current_project_id')
  return stored ? parseInt(stored, 10) : null
}

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    const projectId = getCurrentProject()
    if (projectId) {
      config.headers['X-Project-ID'] = String(projectId)
    }
    return config
  },
  (error) => Promise.reject(error),
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
    return Promise.reject(error)
  },
)

// =============================================================================
// §4.2.2 error envelope
// =============================================================================

export interface ApiErrorBody {
  code: string
  message: string
  field: string | null
  details: unknown
  trace_id: string
}

/** Extract the §4.2.2 `{error: {...}}` body from an axios error (if any). */
export function apiError(err: unknown): ApiErrorBody | null {
  const data = (err as { response?: { data?: unknown } })?.response?.data
  if (data && typeof data === 'object' && 'error' in data) {
    const body = (data as { error?: unknown }).error
    if (body && typeof body === 'object' && 'code' in body) return body as ApiErrorBody
  }
  return null
}

/** True when the server rejected a stale `expected_row_version` (§4.1.3). */
export function isRowVersionConflict(err: unknown): boolean {
  return !!apiError(err)?.code.endsWith('_ROW_VERSION_CONFLICT')
}

/** Human-readable message for any API error (field-located when possible). */
export function apiErrorMessage(err: unknown, fallback?: string): string {
  const body = apiError(err)
  if (body) {
    if (isRowVersionConflict(err)) return i18n.t('common.conflict')
    return body.field ? `${body.field}: ${body.message}` : body.message
  }
  if (err instanceof Error) return err.message
  return fallback ?? i18n.t('common.error')
}

// =============================================================================
// Shared types
// =============================================================================

/** §4.1.1 audit columns + §4.1.3 optimistic lock carried by tenant data. */
export interface Versioned {
  row_version: number
  created_by_id: number | null
  updated_by_id: number | null
  created_at: string
  updated_at: string
}

interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

const unwrap = async <T,>(p: Promise<{ data: Paginated<T> | T[] }>): Promise<T[]> => {
  const r = await p
  const d = r.data as Paginated<T> | T[]
  if (Array.isArray(d)) return d
  return d.results
}

/**
 * Updates must send the `row_version` the client last read (§4.1.3). Callers
 * pass the loaded object (with `row_version`); this maps it to
 * `expected_row_version` unless set explicitly.
 */
const withVersion = <T extends { row_version?: number; expected_row_version?: number }>(
  data: T,
): T => {
  if (data.expected_row_version === undefined && data.row_version !== undefined) {
    return { ...data, expected_row_version: data.row_version }
  }
  return data
}

type VersionedUpdate<T> = Partial<T> & { expected_row_version?: number }

export interface HealthCheckResponse {
  status: string
  version: string
  services: {
    database: string
    cache: string
  }
}

export const healthCheck = async (): Promise<HealthCheckResponse> => {
  const response = await api.get<HealthCheckResponse>('/health/')
  return response.data
}

// =============================================================================
// Authentication (§5.4.1) and current user (§15.7)
// =============================================================================

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
}

/** `{resource: [create|read|update|delete]}` — §15.2.4 matrix. */
export type PermissionMatrix = Record<string, string[]>

export interface UserProfile {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  organization: number | null
  organization_name: string | null
  role: number | null
  role_name: string | null
  role_code: string | null
  role_level: number | null
  is_superuser: boolean
  is_staff: boolean
  phone: string
  department: string
  title: string
  employee_id: string
  language: string
  timezone: string
  avatar: string | null
  is_active: boolean
  date_joined: string
  last_login: string | null
  /** Effective permission matrix (only on /me/). */
  permissions?: PermissionMatrix
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/auth/login/', data)
    return response.data
  },

  refresh: async (refresh: string): Promise<{ access: string }> => {
    const response = await api.post<{ access: string }>('/auth/refresh/', { refresh })
    return response.data
  },

  me: async (): Promise<UserProfile> => {
    const response = await api.get<UserProfile>('/me/')
    return response.data
  },
}

// =============================================================================
// User preferences (I18N-04 / ADM-06)
// =============================================================================

export type UiPreferences = Record<string, unknown>

export const preferencesApi = {
  get: async (): Promise<UiPreferences> => {
    const response = await api.get<UiPreferences>('/me/preferences/')
    return response.data
  },
  patch: async (data: UiPreferences): Promise<UiPreferences> => {
    const response = await api.patch<UiPreferences>('/me/preferences/', data)
    return response.data
  },
}

// =============================================================================
// Roles / users / task forces / audit log (§15.7)
// =============================================================================

export interface Role {
  id: number
  organization: number
  organization_name?: string
  name: string
  code: string
  level: number
  level_display?: string
  description: string
  permissions: PermissionMatrix
  is_system_role: boolean
  display_order: number
  created_at?: string
  updated_at?: string
}

export type TaskForceCreatorRole = 'ADMINISTRATOR' | 'PROJECT_MANAGER' | 'PROJECT_ENGINEER'

export interface ProjectTaskForce {
  id: number
  project_id: number | null
  code: string
  name: string
  description: string
  leader: number | null
  leader_name?: string | null
  created_by: number | null
  created_by_name?: string | null
  created_by_role: TaskForceCreatorRole | ''
  member_count?: number
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface TaskForceMembership {
  id: number
  user: number
  user_name?: string
  user_full_name?: string
  task_force: number
  task_force_name?: string
  /** Overrides the user's system role inside this project (§15.3.1). */
  role_in_project: number | null
  role_in_project_name?: string | null
  joined_at: string
  added_by: number | null
  added_by_name?: string | null
  is_active: boolean
}

export interface AuditLog {
  id: string
  organization: number | null
  project_id: number | null
  user: number | null
  user_name?: string
  action: 'CREATE' | 'READ' | 'UPDATE' | 'DELETE'
  action_display?: string
  model_name: string
  object_id: string
  object_repr: string
  old_values: Record<string, unknown>
  new_values: Record<string, unknown>
  changed_fields: string[]
  change_details: Record<string, unknown>
  batch_id: string | null
  ip_address: string | null
  user_agent: string
  timestamp: string
}

export const organizationCrudApi = {
  list: () => unwrap<Organization>(api.get('/organizations/')),
  get: (id: number) => api.get<Organization>(`/organizations/${id}/`).then((r) => r.data),
  create: (data: Partial<Organization>) =>
    api.post<Organization>('/organizations/', data).then((r) => r.data),
  update: (id: number, data: Partial<Organization>) =>
    api.patch<Organization>(`/organizations/${id}/`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/organizations/${id}/`).then(() => undefined),
}

export const userApi = {
  list: () => unwrap<UserProfile>(api.get('/users/')),
  get: (id: number) => api.get<UserProfile>(`/users/${id}/`).then((r) => r.data),
  create: (data: Partial<UserProfile> & { password?: string; password_confirm?: string }) =>
    api.post<UserProfile>('/users/', data).then((r) => r.data),
  update: (id: number, data: Partial<UserProfile>) =>
    api.patch<UserProfile>(`/users/${id}/`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/users/${id}/`).then(() => undefined),
  activate: (id: number) => api.post(`/users/${id}/activate/`).then((r) => r.data),
  deactivate: (id: number) => api.post(`/users/${id}/deactivate/`).then((r) => r.data),
  resetPassword: (id: number, password: string, passwordConfirm: string) =>
    api
      .post(`/users/${id}/reset-password/`, {
        password,
        password_confirm: passwordConfirm,
      })
      .then((r) => r.data),
}

export const roleApi = {
  list: () => unwrap<Role>(api.get('/roles/')),
  get: (id: number) => api.get<Role>(`/roles/${id}/`).then((r) => r.data),
  create: (data: Partial<Role>) => api.post<Role>('/roles/', data).then((r) => r.data),
  update: (id: number, data: Partial<Role>) =>
    api.patch<Role>(`/roles/${id}/`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/roles/${id}/`).then(() => undefined),
}

export const taskForceApi = {
  list: (projectId?: number) => {
    const params = projectId ? { project_id: projectId } : undefined
    return unwrap<ProjectTaskForce>(api.get('/task-forces/', { params }))
  },
  get: (id: number) => api.get<ProjectTaskForce>(`/task-forces/${id}/`).then((r) => r.data),
  create: (data: Partial<ProjectTaskForce>) =>
    api.post<ProjectTaskForce>('/task-forces/', data).then((r) => r.data),
  update: (id: number, data: Partial<ProjectTaskForce>) =>
    api.patch<ProjectTaskForce>(`/task-forces/${id}/`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/task-forces/${id}/`).then(() => undefined),
  assignProject: (id: number, projectId: number | null) =>
    api
      .post<ProjectTaskForce>(`/task-forces/${id}/assign-project/`, { project_id: projectId })
      .then((r) => r.data),
  members: (id: number) =>
    api.get<TaskForceMembership[]>(`/task-forces/${id}/members/`).then((r) => r.data),
  addMember: (id: number, userId: number, roleInProject: number | null = null) =>
    api
      .post<TaskForceMembership>(`/task-forces/${id}/members/`, {
        user_id: userId,
        role_in_project: roleInProject,
      })
      .then((r) => r.data),
  removeMember: (id: number, userId: number) =>
    api.delete(`/task-forces/${id}/members/${userId}/`).then(() => undefined),
}

export interface MyTaskForce {
  id: number
  code: string
  name: string
  project_id: number | null
  project_no: string | null
  project_name: string | null
}

export const meApi = {
  taskForces: () => api.get<MyTaskForce[]>('/me/task-forces/').then((r) => r.data),
}

export const auditLogApi = {
  list: (params?: { project_id?: number; user?: number; model_name?: string }) =>
    unwrap<AuditLog>(api.get('/audit-logs/', { params })),
}

// =============================================================================
// Organizations (§15.4.7)
// =============================================================================

export interface Organization {
  id: number
  code: string
  slug: string
  name: string
  description: string
  logo: string | null
  settings: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

export const organizationApi = {
  list: () => unwrap<Organization>(api.get('/organizations/')),
  get: async (id: number) => {
    const response = await api.get<Organization>(`/organizations/${id}/`)
    return response.data
  },
}

// =============================================================================
// Projects (§15.1.3 / §15.4.1)
// =============================================================================

export type ProjectStatus = 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'ARCHIVED'

export interface HierarchyLevelConfig {
  name: 'Client' | 'Site' | 'Plant' | 'Area' | 'Unit'
  required?: boolean
  default_name?: string
  default_code?: string
  allow_multiple?: boolean
}

/** §15.4.6 hierarchy configuration (schema_version 1). */
export interface HierarchyConfig {
  schema_version?: number
  template?: 'standard' | 'simple' | 'custom'
  levels?: HierarchyLevelConfig[]
  auto_create_defaults?: boolean
}

export interface ProjectTenant {
  id: number
  project_no: string
  name: string
  schema_name: string
  organization_id: number
  organization_name: string | null
  description: string
  status: ProjectStatus
  start_date: string | null
  end_date: string | null
  hierarchy_config: HierarchyConfig
  created_at: string
  updated_at: string
}

/** @deprecated alias kept for older components; same shape as ProjectTenant. */
export type Project = ProjectTenant

export const projectApi = {
  list: () => unwrap<ProjectTenant>(api.get('/tenants/projects/')),
  get: async (id: number) => {
    const response = await api.get<ProjectTenant>(`/tenants/projects/${id}/`)
    return response.data
  },
}

export const projectTenantApi = {
  list: () => unwrap<ProjectTenant>(api.get('/tenants/projects/')),
  get: (id: number) =>
    api.get<ProjectTenant>(`/tenants/projects/${id}/`).then((r) => r.data),
  // Schema creation + migration runs synchronously on the backend and can
  // take 10-30 seconds.
  create: (data: Partial<ProjectTenant>) =>
    api
      .post<ProjectTenant>('/tenants/projects/', data, { timeout: 60000 })
      .then((r) => r.data),
  update: (id: number, data: Partial<ProjectTenant>) =>
    api
      .patch<ProjectTenant>(`/tenants/projects/${id}/`, data, { timeout: 60000 })
      .then((r) => r.data),
  delete: (id: number) =>
    api.delete(`/tenants/projects/${id}/`, { timeout: 60000 }).then(() => undefined),
  current: () =>
    api
      .get<{ project: ProjectTenant | null }>('/tenants/projects/current/')
      .then((r) => r.data),
}

// =============================================================================
// Project hierarchy (tenant schema, §15.4 / §5.4.3)
// =============================================================================

/** Client is tenant data: no project FK — the schema is the boundary. */
export interface Client extends Versioned {
  id: number
  code: string
  name: string
  contact_person: string
  contact_email: string
  contact_phone: string
  address: string
}

export interface Site extends Versioned {
  id: number
  client: number
  client_name: string
  code: string
  name: string
  location: string
  address: string
  timezone: string
}

export interface Plant extends Versioned {
  id: number
  site: number
  site_name: string
  site_code: string
  code: string
  name: string
  description: string
  capacity: string
  is_active: boolean
  /** id of the Plant's PLANT root node in the MPTT tree (§15.4.5). */
  root_node: number | null
}

export interface PlantHierarchy extends Versioned {
  id: number
  plant: number | null
  name: string
  code: string
  node_type: 'PLANT' | 'AREA' | 'UNIT'
  parent: number | null
  parent_name?: string | null
  description: string
  is_active: boolean
  full_path: string
  children_count?: number
  level?: number
}

const versionedCrud = <T extends { id: number }>(path: string) => ({
  list: (params?: Record<string, unknown>) => unwrap<T>(api.get(path, { params })),
  get: (id: number) => api.get<T>(`${path}${id}/`).then((r) => r.data),
  create: (data: Partial<T>) => api.post<T>(path, data).then((r) => r.data),
  update: (id: number, data: VersionedUpdate<T>) =>
    api.patch<T>(`${path}${id}/`, withVersion(data)).then((r) => r.data),
  delete: (id: number, rowVersion?: number) =>
    api
      .delete(`${path}${id}/`, {
        params: rowVersion ? { expected_row_version: rowVersion } : undefined,
      })
      .then(() => undefined),
})

const clientCrud = versionedCrud<Client>('/clients/')
export const clientApi = {
  ...clientCrud,
  list: () => clientCrud.list(),
}

const siteCrud = versionedCrud<Site>('/sites/')
export const siteApi = {
  ...siteCrud,
  list: (clientId?: number) => siteCrud.list(clientId ? { client: clientId } : undefined),
}

const plantCrud = versionedCrud<Plant>('/plants/')
export const plantApi = {
  ...plantCrud,
  list: (siteId?: number) => plantCrud.list(siteId ? { site: siteId } : undefined),
}

const hierarchyCrud = versionedCrud<PlantHierarchy>('/plant-hierarchy/')
export const plantHierarchyApi = {
  ...hierarchyCrud,
  list: (params?: {
    parent?: number
    plant?: number
    node_type?: string
    is_active?: boolean
    page_size?: number
  }) => hierarchyCrud.list({ page_size: 500, ...params }),
  /** §5.4.3 re-parent a node. */
  move: (id: number, parent: number, rowVersion?: number) =>
    api
      .post<PlantHierarchy>(`/plant-hierarchy/${id}/move/`, {
        parent,
        expected_row_version: rowVersion,
      })
      .then((r) => r.data),
}

// =============================================================================
// Instrument index (tenant schema, §5.4.4)
// =============================================================================

export interface Loop extends Versioned {
  id: number
  loop_tag: string
  function: string
  suffix: string
  unit: number
  unit_name?: string
  unit_code?: string
  description: string
  is_active: boolean
  tags_count?: number
}

export interface InstrumentType extends Versioned {
  id: number
  name: string
  code: string
  category: string
  description: string
  schema_template: Record<string, unknown>
  default_spec_data: Record<string, unknown>
  is_active: boolean
}

export type TagStatus = 'ACTIVE' | 'INACTIVE' | 'PENDING' | 'UNDER_REVIEW'

export interface Tag extends Versioned {
  id: number
  tag_number: string
  unit: number
  unit_name?: string
  unit_code?: string
  loop: number | null
  loop_tag?: string | null
  instrument_type: number
  instrument_type_name?: string
  instrument_type_code?: string
  service: string
  description: string
  spec_data: Record<string, unknown>
  status: TagStatus
  full_tag: string
}

export interface TagListParams {
  unit?: number
  loop?: number
  status?: string
  instrument_type?: number
  /** Hierarchy filters (ADM-02). */
  client?: number
  site?: number
  plant?: number
  /** Any hierarchy node — includes its whole subtree. */
  node?: number
  search?: string
  page?: number
  page_size?: number
}

export const engineeringApi = {
  loops: {
    list: (unitId?: number) => unwrap<Loop>(api.get('/loops/', { params: unitId ? { unit: unitId } : {} })),
  },

  instrumentTypes: {
    list: () => unwrap<InstrumentType>(api.get('/instrument-types/')),
  },

  tags: {
    list: async (params?: TagListParams) => {
      const response = await api.get<Paginated<Tag>>('/instruments/', { params })
      return response.data
    },
    get: async (id: number) => {
      const response = await api.get<Tag>(`/instruments/${id}/`)
      return response.data
    },
    create: async (data: Partial<Tag>) => {
      const response = await api.post<Tag>('/instruments/', data)
      return response.data
    },
    /** Pass the loaded tag's `row_version` (or `expected_row_version`). */
    update: async (id: number, data: VersionedUpdate<Tag>) => {
      const response = await api.patch<Tag>(`/instruments/${id}/`, withVersion(data))
      return response.data
    },
    delete: async (id: number, rowVersion?: number) => {
      await api.delete(`/instruments/${id}/`, {
        params: rowVersion ? { expected_row_version: rowVersion } : undefined,
      })
    },
  },
}

export default api
