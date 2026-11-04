import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  Building2,
  Users,
  Shield,
  Briefcase,
  ScrollText,
  FolderKanban,
  ArrowRight,
  Lock,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { usePermissions } from '@/hooks/usePermissions'
import { cn } from '@/lib/utils'

interface ModuleCard {
  to: string
  /** i18n key under "admin.card" — title is `${titleKey}Title`, description is `${titleKey}Desc` */
  titleKey: string
  icon: React.ComponentType<{ className?: string }>
  required: 'admin' | 'pe'
  visible: (perms: ReturnType<typeof usePermissions>) => boolean
}

const MODULES: ModuleCard[] = [
  {
    to: '/admin/organizations',
    titleKey: 'organizations',
    icon: Building2,
    required: 'admin',
    visible: (p) => p.canManageUsers,
  },
  {
    to: '/admin/projects',
    titleKey: 'projects',
    icon: FolderKanban,
    required: 'pe',
    visible: (p) => p.canManageProjects,
  },
  {
    to: '/admin/users',
    titleKey: 'users',
    icon: Users,
    required: 'admin',
    visible: (p) => p.canManageUsers,
  },
  {
    to: '/admin/roles',
    titleKey: 'roles',
    icon: Shield,
    required: 'admin',
    visible: (p) => p.canManageUsers,
  },
  {
    to: '/admin/task-forces',
    titleKey: 'taskForces',
    icon: Briefcase,
    required: 'pe',
    visible: (p) => p.canManageTaskForces,
  },
  {
    to: '/admin/audit-logs',
    titleKey: 'auditLogs',
    icon: ScrollText,
    required: 'admin',
    visible: (p) => p.canViewAuditLogs,
  },
]

export function AdminDashboard() {
  const perms = usePermissions()
  const { t } = useTranslation()

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{t('admin.permissionsOverview')}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <Stat
            label={t('admin.stat.role')}
            value={perms.roleName || t('admin.role.unassigned')}
            hint={`Level ${perms.level}`}
          />
          <Stat label={t('admin.stat.discipline')} value={disciplineLabel(perms, t)} />
          <Stat
            label={t('admin.stat.accessibleModules')}
            value={String(MODULES.filter((m) => m.visible(perms)).length)}
            hint={`/ ${MODULES.length}`}
          />
        </CardContent>
      </Card>

      <ModuleSection
        title={t('admin.section.systemAdminTitle')}
        description={t('admin.section.systemAdminDesc')}
        modules={MODULES.filter((m) => m.required === 'admin')}
        perms={perms}
      />

      <ModuleSection
        title={t('admin.section.projectsAndTeamTitle')}
        description={t('admin.section.projectsAndTeamDesc')}
        modules={MODULES.filter((m) => m.required === 'pe')}
        perms={perms}
      />
    </div>
  )
}

function ModuleSection({
  title,
  description,
  modules,
  perms,
}: {
  title: string
  description: string
  modules: ModuleCard[]
  perms: ReturnType<typeof usePermissions>
}) {
  const { t } = useTranslation()
  if (modules.length === 0) return null
  return (
    <section className="space-y-3">
      <div>
        <h2 className="text-base font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {modules.map((m) => {
          const allowed = m.visible(perms)
          return (
            <Card
              key={m.to}
              className={cn(
                'group relative transition-all',
                allowed ? 'hover:border-primary/50 hover:shadow-md' : 'opacity-60',
              )}
            >
              <CardContent className="p-5">
                <div className="mb-3 flex items-start justify-between">
                  <div
                    className={cn(
                      'rounded-lg p-2',
                      allowed ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground',
                    )}
                  >
                    <m.icon className="h-5 w-5" />
                  </div>
                  {!allowed ? (
                    <Badge variant="secondary" className="gap-1">
                      <Lock className="h-3 w-3" />
                      {t('admin.badge.noPermission')}
                    </Badge>
                  ) : (
                    <Badge variant={m.required === 'admin' ? 'destructive' : 'default'}>
                      {m.required === 'admin'
                        ? t('admin.badge.adminOnly')
                        : t('admin.badge.adminOrPe')}
                    </Badge>
                  )}
                </div>
                <h3 className="mb-1 font-semibold">{t(`admin.card.${m.titleKey}Title`)}</h3>
                <p className="mb-4 text-sm text-muted-foreground">
                  {t(`admin.card.${m.titleKey}Desc`)}
                </p>
                {allowed ? (
                  <Link
                    to={m.to}
                    className="inline-flex items-center gap-1 text-sm font-medium text-primary hover:underline"
                  >
                    {t('common.openModule')} <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                ) : (
                  <span className="text-sm text-muted-foreground">
                    {t('common.needHigherPrivilege')}
                  </span>
                )}
              </CardContent>
            </Card>
          )
        })}
      </div>
    </section>
  )
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-md border bg-muted/30 p-3">
      <div className="text-xs uppercase text-muted-foreground">{label}</div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="text-lg font-semibold">{value}</span>
        {hint && <span className="text-xs text-muted-foreground">{hint}</span>}
      </div>
    </div>
  )
}

/** Disciplines the user may write, derived from the permission matrix (D5). */
function disciplineLabel(
  perms: ReturnType<typeof usePermissions>,
  t: (key: string) => string,
): string {
  const writable = [
    perms.canEditInstrumentation && t('admin.discipline.instrumentation'),
    perms.canEditProcess && t('admin.discipline.process'),
    perms.canEditMechanical && t('admin.discipline.mechanical'),
  ].filter(Boolean)
  return writable.length ? writable.join(' / ') : t('admin.discipline.generic')
}
