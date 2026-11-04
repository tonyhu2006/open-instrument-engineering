import { ShieldAlert } from 'lucide-react'
import { Navigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useCurrentUser } from '@/contexts/CurrentUserContext'
import { usePermissions } from '@/hooks/usePermissions'

interface RoleGuardProps {
  /** Required minimum role level (e.g. 5 = Admin, 4 = PE). */
  minLevel?: number
  /** Required permission flag from usePermissions. */
  require?: keyof ReturnType<typeof usePermissions>
  /** Custom predicate; receives permissions object. */
  predicate?: (perms: ReturnType<typeof usePermissions>) => boolean
  /** Behaviour on denial: 'forbidden' renders a 403 panel, 'redirect' goes to /. */
  fallback?: 'forbidden' | 'redirect'
  children: React.ReactNode
}

export function RoleGuard({
  minLevel,
  require,
  predicate,
  fallback = 'forbidden',
  children,
}: RoleGuardProps) {
  const { loading } = useCurrentUser()
  const perms = usePermissions()
  const { t } = useTranslation()

  if (loading) {
    return (
      <div className="flex h-full min-h-[200px] items-center justify-center text-muted-foreground">
        {t('common.loading')}
      </div>
    )
  }

  let allowed = perms.isAuthenticated
  if (allowed && minLevel !== undefined) allowed = perms.level >= minLevel
  if (allowed && require) {
    const v = perms[require]
    allowed = typeof v === 'boolean' ? v : !!v
  }
  if (allowed && predicate) allowed = predicate(perms)

  if (!allowed) {
    if (fallback === 'redirect') return <Navigate to="/" replace />
    return (
      <div className="flex h-full min-h-[60vh] flex-col items-center justify-center gap-3 text-center">
        <ShieldAlert className="h-12 w-12 text-destructive" />
        <h2 className="text-xl font-semibold">{t('admin.guard.deniedTitle')}</h2>
        <p className="max-w-md text-sm text-muted-foreground">
          {t('admin.guard.deniedBody')} ({perms.roleName || t('admin.role.unassigned')})
        </p>
      </div>
    )
  }

  return <>{children}</>
}
