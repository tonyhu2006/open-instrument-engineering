import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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
    
    // Add project ID header for tenant switching
    const projectId = getCurrentProject()
    if (projectId) {
      config.headers['X-Project-ID'] = String(projectId)
    }
    
    return config
  },
  (error) => Promise.reject(error)
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
    return Promise.reject(error)
  }
)

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
// Authentication API
// =============================================================================

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
}

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
  language: string
  timezone: string
  avatar: string | null
  is_active: boolean
  date_joined: string
  last_login: string | null
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post<LoginResponse>('/token/', data)
    return response.data
  },
  
  refresh: async (refresh: string): Promise<{ access: string }> => {
    const response = await api.post<{ access: string }>('/token/refresh/', { refresh })
    return response.data
  },
  
  me: async (): Promise<UserProfile> => {
    const response = await api.get<UserProfile>('/admin/users/me/')
    return response.data
  },
}

// =============================================================================
// User UI Preferences API
// =============================================================================

export type UiPreferences = Record<string, unknown>

export const preferencesApi = {
  get: async (): Promise<UiPreferences> => {
    const response = await api.get<UiPreferences>('/admin/users/me/preferences/')
    return response.data
  },
  patch: async (data: UiPreferences): Promise<UiPreferences> => {
    const response = await api.patch<UiPreferences>('/admin/users/me/preferences/', data)
    return response.data
  },
}

// =============================================================================
// Role / User / Membership / Task Force / Audit Log APIs
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
  permissions: Record<string, string[]>
  is_system_role: boolean
  created_at?: string
  updated_at?: string
}

export interface ProjectTaskForce {
  id: number
  project_id: number
  code: string
  name: string
  description: string
  leader: number | null
  leader_name?: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface TaskForceMembership {
  id: number
  user: number
  user_name?: string
  task_force: number
  task_force_name?: string
  role: string
  joined_at?: string
}

export interface AuditLog {
  id: number
  organization: number | null
  organization_name?: string
  project_id: number | null
  user: number | null
  user_name?: string
  action: string
  model_name: string
  object_id: string
  object_repr: string
  changes: Record<string, unknown>
  ip_address: string | null
  timestamp: string
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

export const organizationCrudApi = {
  list: () => unwrap<Organization>(api.get('/admin/organizations/')),
  get: (id: number) => api.get<Organization>(`/admin/organizations/${id}/`).then(r => r.data),
  create: (data: Partial<Organization>) => api.post<Organization>('/admin/organizations/', data).then(r => r.data),
  update: (id: number, data: Partial<Organization>) => api.patch<Organization>(`/admin/organizations/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/admin/organizations/${id}/`).then(() => undefined),
}

export const userApi = {
  list: () => unwrap<UserProfile>(api.get('/admin/users/')),
  get: (id: number) => api.get<UserProfile>(`/admin/users/${id}/`).then(r => r.data),
  create: (data: Partial<UserProfile> & { password?: string }) =>
    api.post<UserProfile>('/admin/users/', data).then(r => r.data),
  update: (id: number, data: Partial<UserProfile>) =>
    api.patch<UserProfile>(`/admin/users/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/admin/users/${id}/`).then(() => undefined),
  activate: (id: number) => api.post(`/admin/users/${id}/activate/`).then(r => r.data),
  deactivate: (id: number) => api.post(`/admin/users/${id}/deactivate/`).then(r => r.data),
}

export const roleApi = {
  list: () => unwrap<Role>(api.get('/admin/roles/')),
  get: (id: number) => api.get<Role>(`/admin/roles/${id}/`).then(r => r.data),
  create: (data: Partial<Role>) => api.post<Role>('/admin/roles/', data).then(r => r.data),
  update: (id: number, data: Partial<Role>) => api.patch<Role>(`/admin/roles/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/admin/roles/${id}/`).then(() => undefined),
}

export const taskForceApi = {
  list: (projectId?: number) => {
    const params = projectId ? { project_id: projectId } : undefined
    return unwrap<ProjectTaskForce>(api.get('/admin/task-forces/', { params }))
  },
  get: (id: number) => api.get<ProjectTaskForce>(`/admin/task-forces/${id}/`).then(r => r.data),
  create: (data: Partial<ProjectTaskForce>) =>
    api.post<ProjectTaskForce>('/admin/task-forces/', data).then(r => r.data),
  update: (id: number, data: Partial<ProjectTaskForce>) =>
    api.patch<ProjectTaskForce>(`/admin/task-forces/${id}/`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/admin/task-forces/${id}/`).then(() => undefined),
  members: (id: number) => api.get<TaskForceMembership[]>(`/admin/task-forces/${id}/members/`).then(r => r.data),
  addMember: (id: number, userId: number, role = 'member') =>
    api.post(`/admin/task-forces/${id}/add_member/`, { user_id: userId, role }).then(r => r.data),
  removeMember: (id: number, userId: number) =>
    api.post(`/admin/task-forces/${id}/remove_member/`, { user_id: userId }).then(r => r.data),
}

export const auditLogApi = {
  list: (params?: { project_id?: number; user?: number; model_name?: string }) =>
    unwrap<AuditLog>(api.get('/admin/audit-logs/', { params })),
}

// =============================================================================
// Organization API
// =============================================================================

export interface Organization {
  id: number
  code: string
  name: string
  description: string
  logo: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export const organizationApi = {
  list: async () => {
    const response = await api.get<{ results: Organization[] }>('/admin/organizations/')
    return response.data.results
  },
  get: async (id: number) => {
    const response = await api.get<Organization>(`/admin/organizations/${id}/`)
    return response.data
  },
}

// =============================================================================
// Project API
// =============================================================================

export interface Project {
  id: number
  organization: number
  organization_name: string
  project_no: string
  name: string
  description: string
  status: 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED'
  start_date: string | null
  end_date: string | null
  hierarchy_config: Record<string, unknown>
  created_at: string
  updated_at: string
}

/**
 * Client model is tenant-specific (lives in the project schema).
 * It has NO `project` FK — schema isolation handles that. The optional
 * `project` / `project_no` fields are kept for legacy callers but are
 * never populated by the backend serializer.
 */
export interface Client {
  id: number
  project?: number
  project_no?: string
  code: string
  name: string
  contact_person: string
  contact_email: string
  contact_phone: string
  address: string
  created_at: string
  updated_at: string
}

export interface Site {
  id: number
  client: number
  client_name: string
  project_no?: string
  code: string
  name: string
  location: string
  address: string
  timezone: string
  created_at: string
  updated_at: string
}

export interface Plant {
  id: number
  site: number
  site_name: string
  site_code: string
  code: string
  name: string
  description: string
  capacity: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export const projectApi = {
  list: async () => {
    const response = await api.get<{ results: Project[] } | Project[]>('/tenants/projects/')
    const data = response.data
    return Array.isArray(data) ? data : data.results
  },
  get: async (id: number) => {
    const response = await api.get<Project>(`/tenants/projects/${id}/`)
    return response.data
  },
  hierarchy: async (id: number) => {
    const response = await api.get(`/tenants/projects/${id}/hierarchy/`)
    return response.data
  },
}

// =============================================================================
// Project Tenant API (CRUD for engineering projects with schema isolation)
// =============================================================================

export interface ProjectTenant {
  id: number
  project_no: string
  name: string
  schema_name: string
  organization_id: number
  organization_name: string | null
  description: string
  status: 'ACTIVE' | 'ON_HOLD' | 'COMPLETED' | 'CANCELLED'
  start_date: string | null
  end_date: string | null
  hierarchy_config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export const projectTenantApi = {
  list: () => unwrap<ProjectTenant>(api.get('/tenants/projects/')),
  get: (id: number) =>
    api.get<ProjectTenant>(`/tenants/projects/${id}/`).then((r) => r.data),
  // Schema creation + migration runs synchronously on the backend and can
  // take 10-30 seconds. Pass extended timeout via the request config so the
  // shared api instance (with JWT / X-Project-ID interceptors) is still used.
  create: (data: Partial<ProjectTenant>) =>
    api
      .post<ProjectTenant>('/tenants/projects/', data, { timeout: 60000 })
      .then((r) => r.data),
  update: (id: number, data: Partial<ProjectTenant>) =>
    api
      .patch<ProjectTenant>(`/tenants/projects/${id}/`, data, { timeout: 60000 })
      .then((r) => r.data),
  delete: (id: number) =>
    api
      .delete(`/tenants/projects/${id}/`, { timeout: 60000 })
      .then(() => undefined),
  current: () =>
    api.get<{ project: ProjectTenant | null }>('/tenants/projects/current/').then((r) => r.data),
}

export const clientApi = {
  list: async (projectId?: number) => {
    const params = projectId ? { project: projectId } : {}
    const response = await api.get<{ results: Client[] } | Client[]>('/engineering/clients/', { params })
    const data = response.data
    return Array.isArray(data) ? data : data.results
  },
  get: (id: number) => api.get<Client>(`/engineering/clients/${id}/`).then((r) => r.data),
  create: (data: Partial<Client>) =>
    api.post<Client>('/engineering/clients/', data).then((r) => r.data),
  update: (id: number, data: Partial<Client>) =>
    api.patch<Client>(`/engineering/clients/${id}/`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/engineering/clients/${id}/`).then(() => undefined),
}

export const siteApi = {
  list: async (clientId?: number) => {
    const params = clientId ? { client: clientId } : {}
    const response = await api.get<{ results: Site[] } | Site[]>('/engineering/sites/', { params })
    const data = response.data
    return Array.isArray(data) ? data : data.results
  },
  get: (id: number) => api.get<Site>(`/engineering/sites/${id}/`).then((r) => r.data),
  create: (data: Partial<Site>) =>
    api.post<Site>('/engineering/sites/', data).then((r) => r.data),
  update: (id: number, data: Partial<Site>) =>
    api.patch<Site>(`/engineering/sites/${id}/`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/engineering/sites/${id}/`).then(() => undefined),
}

export const plantApi = {
  list: async (siteId?: number) => {
    const params = siteId ? { site: siteId } : {}
    const response = await api.get<{ results: Plant[] } | Plant[]>('/engineering/plants/', { params })
    const data = response.data
    return Array.isArray(data) ? data : data.results
  },
  get: (id: number) => api.get<Plant>(`/engineering/plants/${id}/`).then((r) => r.data),
  create: (data: Partial<Plant>) =>
    api.post<Plant>('/engineering/plants/', data).then((r) => r.data),
  update: (id: number, data: Partial<Plant>) =>
    api.patch<Plant>(`/engineering/plants/${id}/`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/engineering/plants/${id}/`).then(() => undefined),
}

// PlantHierarchy MPTT API (PLANT root → AREA → UNIT). The MPTT tree is
// stored in the tenant schema and is conventionally linked to a Plant by
// matching `code` (no foreign key).
export const plantHierarchyApi = {
  list: async (params?: { parent?: number; node_type?: string; is_active?: boolean }) => {
    const response = await api.get<{ results: PlantHierarchy[] } | PlantHierarchy[]>(
      '/engineering/hierarchy/',
      { params },
    )
    const data = response.data
    return Array.isArray(data) ? data : data.results
  },
  get: (id: number) =>
    api.get<PlantHierarchy>(`/engineering/hierarchy/${id}/`).then((r) => r.data),
  create: (data: Partial<PlantHierarchy>) =>
    api.post<PlantHierarchy>('/engineering/hierarchy/', data).then((r) => r.data),
  update: (id: number, data: Partial<PlantHierarchy>) =>
    api.patch<PlantHierarchy>(`/engineering/hierarchy/${id}/`, data).then((r) => r.data),
  delete: (id: number) =>
    api.delete(`/engineering/hierarchy/${id}/`).then(() => undefined),
}

// =============================================================================
// Engineering API (Tags, Loops, etc.)
// =============================================================================

export interface PlantHierarchy {
  id: number
  name: string
  code: string
  node_type: 'PLANT' | 'AREA' | 'UNIT'
  parent: number | null
  description: string
  is_active: boolean
  full_path: string
  created_at: string
  updated_at: string
}

export interface Loop {
  id: number
  loop_tag: string
  function: string
  suffix: string
  unit: number
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface InstrumentType {
  id: number
  name: string
  code: string
  category: string
  description: string
  schema_template: Record<string, unknown>
  default_spec_data: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Tag {
  id: number
  tag_number: string
  unit: number
  loop: number | null
  instrument_type: number
  service: string
  description: string
  spec_data: Record<string, unknown>
  status: 'ACTIVE' | 'INACTIVE' | 'DELETED' | 'PENDING' | 'UNDER_REVIEW'
  revision: number
  full_tag: string
  created_at: string
  updated_at: string
}

export const engineeringApi = {
  // Plant Hierarchy
  hierarchies: {
    list: async () => {
      const response = await api.get<{ results: PlantHierarchy[] } | PlantHierarchy[]>('/engineering/hierarchy/')
      const data = response.data
      return Array.isArray(data) ? data : data.results
    },
    get: async (id: number) => {
      const response = await api.get<PlantHierarchy>(`/engineering/hierarchy/${id}/`)
      return response.data
    },
  },
  
  // Loops
  loops: {
    list: async (unitId?: number) => {
      const params = unitId ? { unit: unitId } : {}
      const response = await api.get<{ results: Loop[] }>('/engineering/loops/', { params })
      return response.data.results
    },
  },
  
  // Instrument Types
  instrumentTypes: {
    list: async () => {
      const response = await api.get<{ results: InstrumentType[] }>('/engineering/instrument-types/')
      return response.data.results
    },
  },
  
  // Tags
  tags: {
    list: async (params?: { unit?: number; loop?: number; status?: string; plant?: number; site?: number; client?: number; project?: number }) => {
      const response = await api.get<{ results: Tag[]; count: number }>('/engineering/tags/', { params })
      return response.data
    },
    get: async (id: number) => {
      const response = await api.get<Tag>(`/engineering/tags/${id}/`)
      return response.data
    },
    create: async (data: Partial<Tag>) => {
      const response = await api.post<Tag>('/engineering/tags/', data)
      return response.data
    },
    update: async (id: number, data: Partial<Tag>) => {
      const response = await api.patch<Tag>(`/engineering/tags/${id}/`, data)
      return response.data
    },
    delete: async (id: number) => {
      await api.delete(`/engineering/tags/${id}/`)
    },
    bulkUpdate: async (data: { ids: number[]; updates: Partial<Tag> }) => {
      const response = await api.post('/engineering/tags/bulk-update/', data)
      return response.data
    },
    search: async (query: string) => {
      const response = await api.get<{ results: Tag[] }>('/engineering/tags/search/', { params: { q: query } })
      return response.data.results
    },
  },
}

export default api
