import { Outlet } from 'react-router-dom'
import { ResizableSidebar } from './ResizableSidebar'
import { Header } from './Header'
import { HierarchyProvider } from '@/components/hierarchy'
import { CurrentUserProvider } from '@/contexts/CurrentUserContext'

export function MainLayout() {
  return (
    <CurrentUserProvider>
      <HierarchyProvider>
        <div className="flex h-screen overflow-hidden">
          <ResizableSidebar />
          <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
            <Header />
            <main className="flex-1 overflow-auto bg-muted/30 p-6">
              <Outlet />
            </main>
          </div>
        </div>
      </HierarchyProvider>
    </CurrentUserProvider>
  )
}
