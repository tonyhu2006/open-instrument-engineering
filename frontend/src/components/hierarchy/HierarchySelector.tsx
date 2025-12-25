import { useState, useRef, useEffect } from 'react'
import { createPortal } from 'react-dom'
import { ChevronDown, Building2, MapPin, Factory, Layers, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useHierarchy } from './HierarchyContext'

export function HierarchySelector() {
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
    currentPath,
    isLoading,
  } = useHierarchy()

  const [isOpen, setIsOpen] = useState(false)
  const [activeTab, setActiveTab] = useState<'project' | 'client' | 'site' | 'plant'>('project')
  const buttonRef = useRef<HTMLButtonElement>(null)
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0, width: 0 })

  // Update dropdown position when opened
  useEffect(() => {
    if (isOpen && buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect()
      setDropdownPosition({
        top: rect.bottom + 4,
        left: rect.left,
        width: Math.max(rect.width, 280),
      })
    }
  }, [isOpen])

  const tabs = [
    { key: 'project' as const, label: 'Project', icon: Building2, items: projects, selected: selectedProject, onSelect: selectProject },
    { key: 'client' as const, label: 'Client', icon: MapPin, items: clients, selected: selectedClient, onSelect: selectClient },
    { key: 'site' as const, label: 'Site', icon: Factory, items: sites, selected: selectedSite, onSelect: selectSite },
    { key: 'plant' as const, label: 'Plant', icon: Layers, items: plants, selected: selectedPlant, onSelect: selectPlant },
  ]

  return (
    <div className="relative">
      <Button
        ref={buttonRef}
        variant="outline"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full justify-between text-left font-normal"
      >
        <div className="flex items-center gap-2 truncate">
          <Building2 className="h-4 w-4 text-muted-foreground flex-shrink-0" />
          <span className="truncate">{isLoading ? 'Loading...' : currentPath}</span>
        </div>
        <ChevronDown className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </Button>

      {isOpen && createPortal(
        <>
          {/* Backdrop - transparent but catches clicks */}
          <div 
            className="fixed inset-0" 
            style={{ zIndex: 9998 }}
            onClick={() => setIsOpen(false)}
          />
          
          {/* Dropdown - fixed position using Portal */}
          <div 
            className="fixed border rounded-lg shadow-xl overflow-hidden"
            style={{ 
              zIndex: 9999, 
              top: dropdownPosition.top,
              left: dropdownPosition.left,
              width: dropdownPosition.width,
              maxWidth: 'calc(100vw - 2rem)',
              backgroundColor: 'hsl(var(--background))',
            }}
          >
            {/* Tabs */}
            <div className="flex border-b">
              {tabs.map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key)}
                  className={`flex-1 px-3 py-2 text-sm font-medium transition-colors ${
                    activeTab === tab.key
                      ? 'bg-muted text-foreground border-b-2 border-primary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                  }`}
                >
                  <tab.icon className="h-4 w-4 mx-auto mb-1" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Content */}
            <div className="max-h-64 overflow-y-auto">
              {tabs.map((tab) => (
                activeTab === tab.key && (
                  <div key={tab.key} className="p-2">
                    {tab.items.length === 0 ? (
                      <div className="text-center py-4 text-muted-foreground text-sm">
                        {tab.key === 'project' ? 'No projects available' : `Select a ${tabs[tabs.findIndex(t => t.key === tab.key) - 1]?.label.toLowerCase()} first`}
                      </div>
                    ) : (
                      <div className="space-y-1">
                        {tab.items.map((item: { id: number; code?: string; project_no?: string; name: string }) => {
                          const isSelected = tab.selected?.id === item.id
                          const code = 'project_no' in item ? item.project_no : item.code
                          return (
                            <button
                              key={item.id}
                              onClick={() => {
                                tab.onSelect(item as never)
                                // Move to next tab if available
                                const nextTabIndex = tabs.findIndex(t => t.key === tab.key) + 1
                                if (nextTabIndex < tabs.length) {
                                  setActiveTab(tabs[nextTabIndex].key)
                                } else {
                                  setIsOpen(false)
                                }
                              }}
                              className={`w-full flex items-center gap-2 px-3 py-2 rounded-md text-left transition-colors ${
                                isSelected
                                  ? 'bg-primary text-primary-foreground'
                                  : 'hover:bg-muted'
                              }`}
                            >
                              <div className="flex-1 min-w-0">
                                <div className="font-medium truncate">{code}</div>
                                <div className={`text-xs truncate ${isSelected ? 'text-primary-foreground/80' : 'text-muted-foreground'}`}>
                                  {item.name}
                                </div>
                              </div>
                              {isSelected && <Check className="h-4 w-4 flex-shrink-0" />}
                            </button>
                          )
                        })}
                      </div>
                    )}
                  </div>
                )
              ))}
            </div>

            {/* Current Selection Summary */}
            <div className="border-t p-2 bg-muted/30">
              <div className="text-xs text-muted-foreground">
                Current: <span className="font-medium text-foreground">{currentPath}</span>
              </div>
            </div>
          </div>
        </>,
        document.body
      )}
    </div>
  )
}
