import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { MainLayout } from '@/components/layout'
import { ProtectedRoute } from '@/components/auth'
import { Dashboard, StatusPage, LoginPage, InstrumentsPage, TagDetailPage, SettingsPage } from '@/pages'
import {
  AdminLayout,
  AdminDashboard,
  OrganizationsPage,
  ProjectsPage,
  ProjectHierarchyPage,
  UsersPage,
  RolesPage,
  TaskForcesPage,
  TaskForceMembersPage,
  AuditLogsPage,
} from '@/pages/admin'

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-2xl font-bold text-muted-foreground">{title}</h1>
      <p className="text-muted-foreground mt-2">Coming soon...</p>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="status" element={<StatusPage />} />
          <Route path="instruments" element={<InstrumentsPage />} />
          <Route path="instruments/:id" element={<TagDetailPage />} />
          <Route path="loops" element={<PlaceholderPage title="Loops" />} />
          <Route path="specs" element={<PlaceholderPage title="Specification Sheets" />} />
          <Route path="wiring" element={<PlaceholderPage title="Wiring Manager" />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="organizations" element={<OrganizationsPage />} />
            <Route path="projects" element={<ProjectsPage />} />
            <Route path="projects/:id/hierarchy" element={<ProjectHierarchyPage />} />
            <Route path="users" element={<UsersPage />} />
            <Route path="roles" element={<RolesPage />} />
            <Route path="task-forces" element={<TaskForcesPage />} />
            <Route path="task-forces/:id/members" element={<TaskForceMembersPage />} />
            <Route path="audit-logs" element={<AuditLogsPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
