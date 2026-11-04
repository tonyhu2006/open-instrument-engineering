import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Building2,
  Users,
  Shield,
  Briefcase,
  ScrollText,
  LayoutDashboard,
  FolderKanban,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { usePermissions } from '@/hooks/usePermissions'
import { RoleGuard } from '@/components/auth'

interface AdminNavItem {
  to: string
  /** i18n key under "admin.tab" */
  titleKey: string
  icon: React.ComponentType<{ className?: string }>
  visible: (perms: ReturnType<typeof usePermissions>) => boolean
}

const ADMIN_NAV: AdminNavItem[] = [
  {
    to: '/admin',
    titleKey: 'admin.tab.overview',
    icon: LayoutDashboard,
    visible: (p) => p.canAccessAdmin,
  },
  // ---- System administration (admin only) ----
  {
    to: '/admin/organizations',
    titleKey: 'admin.tab.organizations',
    icon: Building2,
    visible: (p) => p.canManageUsers,
  },
  {
    to: '/admin/users',
    titleKey: 'admin.tab.users',
    icon: Users,
    visible: (p) => p.canManageUsers,
  },
  {
    to: '/admin/roles',
    titleKey: 'admin.tab.roles',
    icon: Shield,
    visible: (p) => p.canManageUsers,
  },
  {
    to: '/admin/audit-logs',
    titleKey: 'admin.tab.auditLogs',
    icon: ScrollText,
    visible: (p) => p.canViewAuditLogs,
  },
  // ---- Projects & teams (admin / project engineer) ----
  {
    to: '/admin/projects',
    titleKey: 'admin.tab.projects',
    icon: FolderKanban,
    visible: (p) => p.canManageProjects,
  },
  {
    to: '/admin/task-forces',
    titleKey: 'admin.tab.taskForces',
    icon: Briefcase,
    visible: (p) => p.canManageTaskForces,
  },
]

export function AdminLayout() {
  const perms = usePermissions()
  const location = useLocation()
  const { t } = useTranslation()
  const navItems = ADMIN_NAV.filter((item) => item.visible(perms))

  return (
    <RoleGuard require="canAccessAdmin">
      <div className="flex h-full flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{t('admin.title')}</h1>
            <p className="text-sm text-muted-foreground">
              {t('admin.subtitle')}
            </p>
          </div>
          <div className="flex items-center gap-2 rounded-full border bg-background px-3 py-1.5 text-xs">
            <Shield className="h-3.5 w-3.5" />
            <span className="font-medium">{perms.roleName || t('admin.role.unassigned')}</span>
            <span className="text-muted-foreground">Lv.{perms.level}</span>
          </div>
        </div>

        <div className="flex flex-wrap gap-1 border-b">
          {navItems.map((item) => {
            const isActive =
              item.to === '/admin'
                ? location.pathname === '/admin'
                : location.pathname.startsWith(item.to)
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/admin'}
                className={cn(
                  'flex items-center gap-2 border-b-2 px-4 py-2.5 text-sm font-medium transition-colors -mb-px',
                  isActive
                    ? 'border-primary text-foreground'
                    : 'border-transparent text-muted-foreground hover:border-muted-foreground/30 hover:text-foreground',
                )}
              >
                <item.icon className="h-4 w-4" />
                {t(item.titleKey)}
              </NavLink>
            )
          })}
        </div>

        <div className="flex-1">
          <Outlet />
        </div>
      </div>
    </RoleGuard>
  )
}
