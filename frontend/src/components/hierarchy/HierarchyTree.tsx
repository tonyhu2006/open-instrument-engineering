import { useState } from 'react'
import { ChevronRight, ChevronDown, Building2, MapPin, Factory, Layers } from 'lucide-react'
import { useHierarchy } from './HierarchyContext'

interface TreeNodeProps {
  label: string
  code: string
  icon: React.ElementType
  isSelected: boolean
  isExpanded: boolean
  hasChildren: boolean
  level: number
  onClick: () => void
  onToggle: () => void
}

function TreeNode({ label, code, icon: Icon, isSelected, isExpanded, hasChildren, level, onClick, onToggle }: TreeNodeProps) {
  return (
    <div
      className={`flex items-center gap-1 px-2 py-1.5 rounded-md cursor-pointer transition-colors ${
        isSelected ? 'bg-primary text-primary-foreground' : 'hover:bg-muted'
      }`}
      style={{ paddingLeft: `${level * 16 + 8}px` }}
      onClick={onClick}
    >
      {hasChildren ? (
        <button
          onClick={(e) => {
            e.stopPropagation()
            onToggle()
          }}
          className="p-0.5 hover:bg-black/10 rounded"
        >
          {isExpanded ? (
            <ChevronDown className="h-3 w-3" />
          ) : (
            <ChevronRight className="h-3 w-3" />
          )}
        </button>
      ) : (
        <span className="w-4" />
      )}
      <Icon className={`h-4 w-4 ${isSelected ? '' : 'text-muted-foreground'}`} />
      <span className="font-medium text-sm">{code}</span>
      <span className={`text-xs truncate ${isSelected ? 'text-primary-foreground/80' : 'text-muted-foreground'}`}>
        - {label}
      </span>
    </div>
  )
}

export function HierarchyTree() {
  const {
    projects,
    clients,
    sites,
    plants,
    selectedProject,
    selectedClient,
    selectedSite,
    selectedPlant,
    selectProject,
    selectClient,
    selectSite,
    selectPlant,
    isLoading,
  } = useHierarchy()

  const [expandedProjects, setExpandedProjects] = useState<Set<number>>(new Set())
  const [expandedClients, setExpandedClients] = useState<Set<number>>(new Set())
  const [expandedSites, setExpandedSites] = useState<Set<number>>(new Set())

  const toggleProject = (id: number) => {
    setExpandedProjects(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const toggleClient = (id: number) => {
    setExpandedClients(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const toggleSite = (id: number) => {
    setExpandedSites(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  if (isLoading) {
    return (
      <div className="p-4 text-center text-muted-foreground text-sm">
        Loading hierarchy...
      </div>
    )
  }

  if (projects.length === 0) {
    return (
      <div className="p-4 text-center text-muted-foreground text-sm">
        No projects available
      </div>
    )
  }

  return (
    <div className="py-2">
      {projects.map(project => {
        const isProjectExpanded = expandedProjects.has(project.id)
        const isProjectSelected = selectedProject?.id === project.id
        const projectClients = clients.filter(c => c.project === project.id)

        return (
          <div key={project.id}>
            <TreeNode
              label={project.name}
              code={project.project_no}
              icon={Building2}
              isSelected={isProjectSelected && !selectedClient}
              isExpanded={isProjectExpanded}
              hasChildren={true}
              level={0}
              onClick={() => {
                selectProject(project)
                if (!isProjectExpanded) toggleProject(project.id)
              }}
              onToggle={() => toggleProject(project.id)}
            />

            {isProjectExpanded && isProjectSelected && projectClients.map(client => {
              const isClientExpanded = expandedClients.has(client.id)
              const isClientSelected = selectedClient?.id === client.id
              const clientSites = sites.filter(s => s.client === client.id)

              return (
                <div key={client.id}>
                  <TreeNode
                    label={client.name}
                    code={client.code}
                    icon={MapPin}
                    isSelected={isClientSelected && !selectedSite}
                    isExpanded={isClientExpanded}
                    hasChildren={true}
                    level={1}
                    onClick={() => {
                      selectClient(client)
                      if (!isClientExpanded) toggleClient(client.id)
                    }}
                    onToggle={() => toggleClient(client.id)}
                  />

                  {isClientExpanded && isClientSelected && clientSites.map(site => {
                    const isSiteExpanded = expandedSites.has(site.id)
                    const isSiteSelected = selectedSite?.id === site.id
                    const sitePlants = plants.filter(p => p.site === site.id)

                    return (
                      <div key={site.id}>
                        <TreeNode
                          label={site.name}
                          code={site.code}
                          icon={Factory}
                          isSelected={isSiteSelected && !selectedPlant}
                          isExpanded={isSiteExpanded}
                          hasChildren={sitePlants.length > 0}
                          level={2}
                          onClick={() => {
                            selectSite(site)
                            if (!isSiteExpanded) toggleSite(site.id)
                          }}
                          onToggle={() => toggleSite(site.id)}
                        />

                        {isSiteExpanded && isSiteSelected && sitePlants.map(plant => {
                          const isPlantSelected = selectedPlant?.id === plant.id

                          return (
                            <TreeNode
                              key={plant.id}
                              label={plant.name}
                              code={plant.code}
                              icon={Layers}
                              isSelected={isPlantSelected}
                              isExpanded={false}
                              hasChildren={false}
                              level={3}
                              onClick={() => selectPlant(plant)}
                              onToggle={() => {}}
                            />
                          )
                        })}
                      </div>
                    )
                  })}
                </div>
              )
            })}
          </div>
        )
      })}
    </div>
  )
}
