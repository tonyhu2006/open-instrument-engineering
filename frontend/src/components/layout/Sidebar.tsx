import { useState } from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Tag,
  GitBranch,
  Settings,
  Cable,
  FileText,
  Activity,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { HierarchySelector, HierarchyTree } from '@/components/hierarchy'

interface NavItem {
  title: string
  href: string
  icon: React.ComponentType<{ className?: string }>
}

const navItems: NavItem[] = [
  { title: 'Dashboard', href: '/', icon: LayoutDashboard },
  { title: 'Instrument Index', href: '/instruments', icon: Tag },
  { title: 'Loops', href: '/loops', icon: GitBranch },
  { title: 'Spec Sheets', href: '/specs', icon: FileText },
  { title: 'Wiring', href: '/wiring', icon: Cable },
]

const bottomNavItems: NavItem[] = [
  { title: 'System Status', href: '/status', icon: Activity },
  { title: 'Settings', href: '/settings', icon: Settings },
]

export function Sidebar() {
  const [showHierarchyTree, setShowHierarchyTree] = useState(false)

  return (
    <aside className="flex h-screen w-64 flex-col border-r bg-sidebar text-sidebar-foreground">
      <div className="flex h-16 items-center border-b px-6">
        <h1 className="text-xl font-bold text-sidebar-primary">
          OpenInstrument
        </h1>
      </div>

      {/* Hierarchy Selector */}
      <div className="p-3 border-b">
        <HierarchySelector />
      </div>

      {/* Hierarchy Tree Toggle */}
      <button
        onClick={() => setShowHierarchyTree(!showHierarchyTree)}
        className="flex items-center justify-between px-4 py-2 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors border-b"
      >
        <span>PROJECT HIERARCHY</span>
        {showHierarchyTree ? (
          <ChevronDown className="h-3 w-3" />
        ) : (
          <ChevronRight className="h-3 w-3" />
        )}
      </button>

      {/* Hierarchy Tree */}
      {showHierarchyTree && (
        <div className="max-h-48 overflow-y-auto border-b">
          <HierarchyTree />
        </div>
      )}

      <nav className="flex-1 space-y-1 p-4 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.title}
          </NavLink>
        ))}
      </nav>

      <div className="border-t p-4">
        {bottomNavItems.map((item) => (
          <NavLink
            key={item.href}
            to={item.href}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
              )
            }
          >
            <item.icon className="h-5 w-5" />
            {item.title}
          </NavLink>
        ))}
      </div>
    </aside>
  )
}
