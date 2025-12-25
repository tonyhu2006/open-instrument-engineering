import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  Save, 
  History, 
  Copy,
  Loader2,
  AlertCircle
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { engineeringApi, type Tag } from '@/lib/api'

interface SpecField {
  key: string
  label: string
  type: 'text' | 'number' | 'select' | 'textarea' | 'boolean'
  options?: string[]
  unit?: string
  required?: boolean
  group?: string
}

const defaultSpecFields: SpecField[] = [
  { key: 'manufacturer', label: 'Manufacturer', type: 'text', group: 'General' },
  { key: 'model', label: 'Model', type: 'text', group: 'General' },
  { key: 'range_min', label: 'Range Min', type: 'number', group: 'Process' },
  { key: 'range_max', label: 'Range Max', type: 'number', group: 'Process' },
  { key: 'range_unit', label: 'Range Unit', type: 'select', options: ['°C', '°F', 'bar', 'psi', 'kPa', 'MPa', '%', 'm³/h', 'kg/h'], group: 'Process' },
  { key: 'accuracy', label: 'Accuracy', type: 'text', group: 'Performance' },
  { key: 'output_signal', label: 'Output Signal', type: 'select', options: ['4-20mA', '0-10V', 'HART', 'Modbus', 'Profibus', 'Foundation Fieldbus'], group: 'Electrical' },
  { key: 'power_supply', label: 'Power Supply', type: 'select', options: ['24VDC', '110VAC', '220VAC', 'Loop Powered'], group: 'Electrical' },
  { key: 'enclosure_rating', label: 'Enclosure Rating', type: 'select', options: ['IP65', 'IP66', 'IP67', 'IP68', 'Explosion Proof'], group: 'Mechanical' },
  { key: 'process_connection', label: 'Process Connection', type: 'text', group: 'Mechanical' },
  { key: 'material_wetted', label: 'Wetted Material', type: 'text', group: 'Mechanical' },
  { key: 'notes', label: 'Notes', type: 'textarea', group: 'Other' },
]

export function TagDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  
  const [tag, setTag] = useState<Tag | null>(null)
  const [specData, setSpecData] = useState<Record<string, unknown>>({})
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDirty, setIsDirty] = useState(false)

  useEffect(() => {
    if (id) {
      loadTag(parseInt(id))
    }
  }, [id])

  const loadTag = async (tagId: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await engineeringApi.tags.get(tagId)
      setTag(data)
      setSpecData(data.spec_data || {})
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tag')
    } finally {
      setLoading(false)
    }
  }

  const handleFieldChange = (key: string, value: unknown) => {
    setSpecData(prev => ({ ...prev, [key]: value }))
    setIsDirty(true)
  }

  const handleSave = async () => {
    if (!tag) return
    
    setSaving(true)
    try {
      await engineeringApi.tags.update(tag.id, { spec_data: specData })
      setIsDirty(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  const groupedFields = defaultSpecFields.reduce((acc, field) => {
    const group = field.group || 'Other'
    if (!acc[group]) acc[group] = []
    acc[group].push(field)
    return acc
  }, {} as Record<string, SpecField[]>)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !tag) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <p className="text-red-500 mb-4">{error || 'Tag not found'}</p>
        <Button variant="outline" onClick={() => navigate('/instruments')}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Instruments
        </Button>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/instruments')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-2xl font-bold font-mono">{tag.tag_number}</h1>
            <p className="text-sm text-muted-foreground">{tag.service || 'No service description'}</p>
          </div>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
            tag.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
            tag.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {tag.status}
          </span>
          <span className="text-sm text-muted-foreground">Rev {tag.revision}</span>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <History className="h-4 w-4 mr-2" />
            History
          </Button>
          <Button variant="outline" size="sm">
            <Copy className="h-4 w-4 mr-2" />
            Duplicate
          </Button>
          <Button 
            size="sm" 
            onClick={handleSave} 
            disabled={!isDirty || saving}
          >
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save
          </Button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Basic Info */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Basic Information</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">
                  Tag Number
                </label>
                <input
                  type="text"
                  value={tag.tag_number}
                  disabled
                  className="w-full px-3 py-2 rounded-md border bg-muted"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">
                  Service Description
                </label>
                <input
                  type="text"
                  value={tag.service}
                  disabled
                  className="w-full px-3 py-2 rounded-md border bg-muted"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">
                  Description
                </label>
                <input
                  type="text"
                  value={tag.description}
                  disabled
                  className="w-full px-3 py-2 rounded-md border bg-muted"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-muted-foreground mb-1">
                  Full Tag
                </label>
                <input
                  type="text"
                  value={tag.full_tag}
                  disabled
                  className="w-full px-3 py-2 rounded-md border bg-muted font-mono"
                />
              </div>
            </div>
          </section>

          {/* Dynamic Spec Fields */}
          {Object.entries(groupedFields).map(([groupName, fields]) => (
            <section key={groupName}>
              <h2 className="text-lg font-semibold mb-4">{groupName}</h2>
              <div className="grid grid-cols-2 gap-4">
                {fields.map((field) => (
                  <div key={field.key}>
                    <label className="block text-sm font-medium text-muted-foreground mb-1">
                      {field.label}
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </label>
                    
                    {field.type === 'text' && (
                      <input
                        type="text"
                        value={(specData[field.key] as string) || ''}
                        onChange={(e) => handleFieldChange(field.key, e.target.value)}
                        className="w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    )}
                    
                    {field.type === 'number' && (
                      <input
                        type="number"
                        value={(specData[field.key] as number) || ''}
                        onChange={(e) => handleFieldChange(field.key, parseFloat(e.target.value))}
                        className="w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    )}
                    
                    {field.type === 'select' && (
                      <select
                        value={(specData[field.key] as string) || ''}
                        onChange={(e) => handleFieldChange(field.key, e.target.value)}
                        className="w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-primary bg-background"
                      >
                        <option value="">Select...</option>
                        {field.options?.map((opt) => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    )}
                    
                    {field.type === 'textarea' && (
                      <textarea
                        value={(specData[field.key] as string) || ''}
                        onChange={(e) => handleFieldChange(field.key, e.target.value)}
                        rows={3}
                        className="w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                      />
                    )}
                    
                    {field.type === 'boolean' && (
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={(specData[field.key] as boolean) || false}
                          onChange={(e) => handleFieldChange(field.key, e.target.checked)}
                          className="rounded"
                        />
                        <span className="text-sm">Yes</span>
                      </label>
                    )}
                  </div>
                ))}
              </div>
            </section>
          ))}

          {/* Raw JSON View */}
          <section>
            <h2 className="text-lg font-semibold mb-4">Raw Specification Data</h2>
            <pre className="p-4 rounded-lg bg-muted text-sm overflow-x-auto">
              {JSON.stringify(specData, null, 2)}
            </pre>
          </section>
        </div>
      </div>

      {/* Dirty indicator */}
      {isDirty && (
        <div className="fixed bottom-4 right-4 bg-yellow-100 text-yellow-800 px-4 py-2 rounded-lg shadow-lg flex items-center gap-2">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm font-medium">Unsaved changes</span>
        </div>
      )}
    </div>
  )
}
