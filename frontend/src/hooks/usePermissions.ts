/**
 * Role-based permission hook — mirrors the backend RBAC matrix.
 *
 * SPECIFICATION §15.2.4 / decision D5: authorization is decided by the
 * permission matrix `{resource: [create|read|update|delete]}` that the
 * backend returns on `/api/v1/me/` (`permissions`). The UI never branches on
 * `role_code`; the backend remains the authority (this hook only hides UI).
 */

import { useCurrentUser } from '@/contexts/CurrentUserContext'
import type { PermissionMatrix } from '@/lib/api'

export const ROLE_LEVELS = {
  GUEST: 1,
  ENGINEER_L2: 2,
  ENGINEER_L3: 3,
  PROJECT_ENGINEER: 4,
  ADMINISTRATOR: 5,
} as const

export type Action = 'create' | 'read' | 'update' | 'delete'

export interface Permissions {
  level: number
  roleName: string
  isAuthenticated: boolean
  isAdmin: boolean
  isGuest: boolean
  /** Raw matrix check. */
  can: (resource: string, action: Action) => boolean
  // Module access (which admin sub-pages this user can OPEN)
  canManageUsers: boolean // /admin/users, /admin/roles, /admin/organizations
  canViewAuditLogs: boolean // /admin/audit-logs
  canManageTaskForces: boolean // /admin/task-forces
  canManageProjects: boolean // /admin/projects (+ hierarchy)
  canCreateProjects: boolean
  canDeleteProjects: boolean
  canEditHierarchy: boolean
  canAccessAdmin: boolean // any /admin/* route
  // Engineering data write rules (§15.2.4 rows)
  canEditInstrumentation: boolean
  canEditProcess: boolean
  canEditMechanical: boolean
  /** ADM-TF01: Administrators manage any group, creators their own. */
  canEditOwnTaskForce: (createdBy: number | null | undefined) => boolean
}

const EMPTY: PermissionMatrix = {}

export function usePermissions(): Permissions {
  const { user } = useCurrentUser()

  const isAuthenticated = !!user
  const isSuperuser = !!user?.is_superuser
  const level = isSuperuser ? ROLE_LEVELS.ADMINISTRATOR : (user?.role_level ?? 0)
  const roleName = user?.role_name ?? (isSuperuser ? 'Administrator' : '')
  const matrix = user?.permissions ?? EMPTY
  const isAdmin = level >= ROLE_LEVELS.ADMINISTRATOR

  const can = (resource: string, action: Action): boolean => {
    if (!isAuthenticated) return false
    if (isAdmin) return true
    return (matrix[resource] ?? []).includes(action) || (matrix['*'] ?? []).includes(action)
  }

  const canManageUsers = can('user', 'create')
  const canViewAuditLogs = can('audit_log', 'read')
  const canManageTaskForces = can('task_force', 'create')
  const canManageProjects = can('project', 'update')
  const canEditHierarchy = can('plant_hierarchy', 'update')

  return {
    level,
    roleName,
    isAuthenticated,
    isAdmin,
    isGuest: isAuthenticated && level <= ROLE_LEVELS.GUEST,
    can,
    canManageUsers,
    canViewAuditLogs,
    canManageTaskForces,
    canManageProjects,
    canCreateProjects: can('project', 'create'),
    canDeleteProjects: can('project', 'delete'),
    canEditHierarchy,
    canAccessAdmin:
      canManageUsers || canViewAuditLogs || canManageTaskForces || canManageProjects,
    canEditInstrumentation: can('tag', 'update'),
    canEditProcess: can('process_data', 'update'),
    canEditMechanical: can('pipe_specification', 'update'),
    canEditOwnTaskForce: (createdBy) => {
      if (isAdmin) return true
      return canManageTaskForces && !!user && createdBy === user.id
    },
  }
}
