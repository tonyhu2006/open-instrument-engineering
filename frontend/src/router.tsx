import { createBrowserRouter } from 'react-router-dom'
import { MainLayout } from '@/components/layout'
import { Dashboard, StatusPage } from '@/pages'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <MainLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'status',
        element: <StatusPage />,
      },
      {
        path: 'instruments',
        element: <PlaceholderPage title="Instrument Index" />,
      },
      {
        path: 'loops',
        element: <PlaceholderPage title="Loops" />,
      },
      {
        path: 'specs',
        element: <PlaceholderPage title="Specification Sheets" />,
      },
      {
        path: 'wiring',
        element: <PlaceholderPage title="Wiring Manager" />,
      },
      {
        path: 'hierarchy',
        element: <PlaceholderPage title="Plant Hierarchy" />,
      },
      {
        path: 'settings',
        element: <PlaceholderPage title="Settings" />,
      },
    ],
  },
])

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full">
      <h1 className="text-2xl font-bold text-muted-foreground">{title}</h1>
      <p className="text-muted-foreground mt-2">Coming soon...</p>
    </div>
  )
}
