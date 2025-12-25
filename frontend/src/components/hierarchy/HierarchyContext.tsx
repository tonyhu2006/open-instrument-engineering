import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { projectApi, clientApi, siteApi, plantApi, type Project, type Client, type Site, type Plant } from '@/lib/api'

interface HierarchyState {
  // Data
  projects: Project[]
  clients: Client[]
  sites: Site[]
  plants: Plant[]
  
  // Selected items
  selectedProject: Project | null
  selectedClient: Client | null
  selectedSite: Site | null
  selectedPlant: Plant | null
  
  // Loading states
  isLoading: boolean
  
  // Actions
  selectProject: (project: Project | null) => void
  selectClient: (client: Client | null) => void
  selectSite: (site: Site | null) => void
  selectPlant: (plant: Plant | null) => void
  refreshData: () => Promise<void>
  
  // Computed
  currentPath: string
}

const HierarchyContext = createContext<HierarchyState | null>(null)

export function HierarchyProvider({ children }: { children: ReactNode }) {
  const [projects, setProjects] = useState<Project[]>([])
  const [clients, setClients] = useState<Client[]>([])
  const [sites, setSites] = useState<Site[]>([])
  const [plants, setPlants] = useState<Plant[]>([])
  
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [selectedClient, setSelectedClient] = useState<Client | null>(null)
  const [selectedSite, setSelectedSite] = useState<Site | null>(null)
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null)
  
  const [isLoading, setIsLoading] = useState(false)

  // Check if user is authenticated
  const isAuthenticated = () => !!localStorage.getItem('access_token')

  // Load projects on mount (only if authenticated)
  useEffect(() => {
    if (isAuthenticated()) {
      loadProjects()
    }
  }, [])

  // Load clients when project changes
  useEffect(() => {
    if (selectedProject) {
      loadClients(selectedProject.id)
    } else {
      setClients([])
      setSelectedClient(null)
    }
  }, [selectedProject])

  // Load sites when client changes
  useEffect(() => {
    if (selectedClient) {
      loadSites(selectedClient.id)
    } else {
      setSites([])
      setSelectedSite(null)
    }
  }, [selectedClient])

  // Load plants when site changes
  useEffect(() => {
    if (selectedSite) {
      loadPlants(selectedSite.id)
    } else {
      setPlants([])
      setSelectedPlant(null)
    }
  }, [selectedSite])

  const loadProjects = async () => {
    setIsLoading(true)
    try {
      const data = await projectApi.list()
      setProjects(data)
      // Auto-select first project if available
      if (data.length > 0 && !selectedProject) {
        setSelectedProject(data[0])
      }
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadClients = async (projectId: number) => {
    try {
      const data = await clientApi.list(projectId)
      setClients(data)
      // Auto-select first client if available
      if (data.length > 0) {
        setSelectedClient(data[0])
      }
    } catch (error) {
      console.error('Failed to load clients:', error)
    }
  }

  const loadSites = async (clientId: number) => {
    try {
      const data = await siteApi.list(clientId)
      setSites(data)
      // Auto-select first site if available
      if (data.length > 0) {
        setSelectedSite(data[0])
      }
    } catch (error) {
      console.error('Failed to load sites:', error)
    }
  }

  const loadPlants = async (siteId: number) => {
    try {
      const data = await plantApi.list(siteId)
      setPlants(data)
      // Auto-select first plant if available
      if (data.length > 0) {
        setSelectedPlant(data[0])
      }
    } catch (error) {
      console.error('Failed to load plants:', error)
    }
  }

  const selectProject = (project: Project | null) => {
    setSelectedProject(project)
    setSelectedClient(null)
    setSelectedSite(null)
    setSelectedPlant(null)
  }

  const selectClient = (client: Client | null) => {
    setSelectedClient(client)
    setSelectedSite(null)
    setSelectedPlant(null)
  }

  const selectSite = (site: Site | null) => {
    setSelectedSite(site)
    setSelectedPlant(null)
  }

  const selectPlant = (plant: Plant | null) => {
    setSelectedPlant(plant)
  }

  const refreshData = async () => {
    await loadProjects()
  }

  // Compute current path
  const currentPath = [
    selectedProject?.project_no,
    selectedClient?.code,
    selectedSite?.code,
    selectedPlant?.code,
  ].filter(Boolean).join(' / ') || 'Select Project'

  return (
    <HierarchyContext.Provider value={{
      projects,
      clients,
      sites,
      plants,
      selectedProject,
      selectedClient,
      selectedSite,
      selectedPlant,
      isLoading,
      selectProject,
      selectClient,
      selectSite,
      selectPlant,
      refreshData,
      currentPath,
    }}>
      {children}
    </HierarchyContext.Provider>
  )
}

export function useHierarchy() {
  const context = useContext(HierarchyContext)
  if (!context) {
    throw new Error('useHierarchy must be used within a HierarchyProvider')
  }
  return context
}
