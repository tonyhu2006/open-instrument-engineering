/**
 * Role-based permission hook mirroring backend RBAC matrix.
 *
 * Levels:
 *   5 = Administrator        — full access, including user/role/audit mgmt
 *   4 = Project Manager / Project Engineer — full project access, can create task forces
 *   3 = Engineer (discipline) — discipline-specific CRUD, others read
 *   2 = Engineer L2
 *   1 = Guest                — read only
 */

import { useCurrentUser } from '@/contexts/CurrentUserContext'

export const ROLE_LEVELS = {
  GUEST: 1,
  ENGINEER_L2: 2,
  ENGINEER_L3: 3,
  PROJECT_ENGINEER: 4,
  ADMINISTRATOR: 5,
} as const

export type Discipline = 'INSTRUMENTATION' | 'PROCESS' | 'MECHANICAL' | 'GENERIC'

const INSTRUMENT_CODES = new Set(['INST_ENG', 'INSTRUMENTATION', 'INSTRUMENT_ENGINEER', 'INSTR_ENG'])
const PROCESS_CODES = new Set(['PROC_ENG', 'PROCESS', 'PROCESS_ENGINEER'])
const MECHANICAL_CODES = new Set(['MECH_ENG', 'MECHANICAL', 'MECHANICAL_ENGINEER', 'PIPE_ENG'])

export interface Permissions {
  level: number
  roleCode: string
  roleName: string
  isAuthenticated: boolean
  // Identity helpers
  isAdmin: boolean
  isProjectEngineer: boolean
  isEngineer: boolean
  isGuest: boolean
  discipline: Discipline
  // Module access (which admin sub-pages this user can OPEN)
  canManageUsers: boolean        // /admin/users, /admin/roles, /admin/organizations
  canViewAuditLogs: boolean      // /admin/audit-logs
  canManageTaskForces: boolean   // /admin/task-forces
  canManageProjects: boolean     // /admin/projects (Level 4+ Project Manager / PE / Admin)
  canAccessAdmin: boolean        // any /admin/* route
  // Engineering data write rules
  canEditInstrumentation: boolean
  canEditProcess: boolean
  canEditMechanical: boolean
  // Helpers
  canEditOwnTaskForce: (leaderId: number | null | undefined) => boolean
}

function getDiscipline(roleCode: string): Discipline {
  const code = roleCode.toUpperCase()
  if (INSTRUMENT_CODES.has(code)) return 'INSTRUMENTATION'
  if (PROCESS_CODES.has(code)) return 'PROCESS'
  if (MECHANICAL_CODES.has(code)) return 'MECHANICAL'
  return 'GENERIC'
}

export function usePermissions(): Permissions {
  const { user } = useCurrentUser()

  const isAuthenticated = !!user
  // Treat Django superuser as Administrator regardless of role assignment
  const isSuperuser = !!user?.is_superuser
  const baseLevel = user?.role_level ?? 0
  const level = isSuperuser ? ROLE_LEVELS.ADMINISTRATOR : baseLevel
  const roleCode = user?.role_code ?? ''
  const roleName = user?.role_name ?? (isSuperuser ? 'Administrator' : '')
  const discipline = getDiscipline(roleCode)

  const isAdmin = level >= ROLE_LEVELS.ADMINISTRATOR
  const isProjectEngineer = level >= ROLE_LEVELS.PROJECT_ENGINEER
  const isEngineer = level >= ROLE_LEVELS.ENGINEER_L3
  const isGuest = isAuthenticated && level <= ROLE_LEVELS.GUEST

  return {
    level,
    roleCode,
    roleName,
    isAuthenticated,
    isAdmin,
    isProjectEngineer,
    isEngineer,
    isGuest,
    discipline,
    canManageUsers: isAdmin,
    canViewAuditLogs: isAdmin,
    canManageTaskForces: isProjectEngineer,
    canManageProjects: isProjectEngineer,
    canAccessAdmin: isProjectEngineer,
    canEditInstrumentation: isProjectEngineer || (isEngineer && discipline === 'INSTRUMENTATION'),
    canEditProcess: isProjectEngineer || (isEngineer && discipline === 'PROCESS'),
    canEditMechanical: isProjectEngineer || (isEngineer && discipline === 'MECHANICAL'),
    canEditOwnTaskForce: (leaderId) => {
      if (isAdmin) return true
      if (isProjectEngineer && user && leaderId === user.id) return true
      return false
    },
  }
}
