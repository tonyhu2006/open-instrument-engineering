import { useNavigate, useLocation } from 'react-router-dom'
import { Bell, LogOut, User, ShieldCheck } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useCurrentUser } from '@/contexts/CurrentUserContext'

// Map route paths → page title shown in the header.
// Order matters: longest/most-specific prefix first.
const ROUTE_TITLES: Array<[RegExp, string]> = [
  [/^\/admin\/organizations(?:\/|$)/, 'Administration · Organizations'],
  [/^\/admin\/projects\/[^/]+\/hierarchy(?:\/|$)/, 'Administration · Project Hierarchy'],
  [/^\/admin\/projects(?:\/|$)/, 'Administration · Engineering Projects'],
  [/^\/admin\/users(?:\/|$)/, 'Administration · Users'],
  [/^\/admin\/roles(?:\/|$)/, 'Administration · Roles & Permissions'],
  [/^\/admin\/task-forces(?:\/|$)/, 'Administration · Task Forces'],
  [/^\/admin\/audit-logs(?:\/|$)/, 'Administration · Audit Logs'],
  [/^\/admin(?:\/|$)/, 'Administration'],
  [/^\/instruments\/[^/]+/, 'Instrument Detail'],
  [/^\/instruments(?:\/|$)/, 'Instrument Index'],
  [/^\/loops(?:\/|$)/, 'Loops'],
  [/^\/specs(?:\/|$)/, 'Specification Sheets'],
  [/^\/wiring(?:\/|$)/, 'Wiring Manager'],
  [/^\/status(?:\/|$)/, 'System Status'],
  [/^\/settings(?:\/|$)/, 'Settings'],
  [/^\/$/, 'Dashboard'],
]

function resolveTitle(pathname: string): string {
  for (const [pattern, title] of ROUTE_TITLES) {
    if (pattern.test(pathname)) return title
  }
  return 'Dashboard'
}

export function Header() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, loading } = useCurrentUser()

  const pageTitle = resolveTitle(location.pathname)

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    navigate('/login')
  }

  // Format: "username (full name)" — falls back gracefully when either is missing.
  const displayName = (() => {
    if (!user) return loading ? 'Loading...' : 'Not signed in'
    const fullName = user.full_name?.trim()
    if (fullName && fullName !== user.username) {
      return `${user.username} (${fullName})`
    }
    return user.username
  })()

  const roleLabel = user?.is_superuser
    ? 'Administrator'
    : user?.role_name || (user ? 'Unassigned' : '')

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <div className="flex items-center gap-4">
        <h2 className="text-lg font-semibold">{pageTitle}</h2>
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm">
          <div
            className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-muted"
            title={user ? `${user.username} · ${roleLabel}` : undefined}
          >
            <User className="h-4 w-4" />
            <span className="font-medium">{displayName}</span>
            {roleLabel && (
              <span className="flex items-center gap-1 border-l border-border/60 pl-2 text-xs text-muted-foreground">
                <ShieldCheck className="h-3 w-3" />
                {roleLabel}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon">
            <Bell className="h-5 w-5" />
          </Button>
          <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
            <LogOut className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </header>
  )
}
