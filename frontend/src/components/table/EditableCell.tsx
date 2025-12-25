import { useState, useEffect, useRef } from 'react'
import { Check, X } from 'lucide-react'

interface EditableCellProps {
  value: string
  rowId: number
  columnId: string
  onSave: (rowId: number, columnId: string, value: string) => Promise<void>
  type?: 'text' | 'number' | 'select'
  options?: string[]
  disabled?: boolean
}

export function EditableCell({
  value: initialValue,
  rowId,
  columnId,
  onSave,
  type = 'text',
  options = [],
  disabled = false,
}: EditableCellProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [value, setValue] = useState(initialValue)
  const [isSaving, setIsSaving] = useState(false)
  const inputRef = useRef<HTMLInputElement | HTMLSelectElement>(null)

  useEffect(() => {
    setValue(initialValue)
  }, [initialValue])

  useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus()
      if (inputRef.current instanceof HTMLInputElement) {
        inputRef.current.select()
      }
    }
  }, [isEditing])

  const handleDoubleClick = () => {
    if (!disabled) {
      setIsEditing(true)
    }
  }

  const handleSave = async () => {
    if (value !== initialValue) {
      setIsSaving(true)
      try {
        await onSave(rowId, columnId, value)
      } catch (error) {
        setValue(initialValue) // Revert on error
      } finally {
        setIsSaving(false)
      }
    }
    setIsEditing(false)
  }

  const handleCancel = () => {
    setValue(initialValue)
    setIsEditing(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave()
    } else if (e.key === 'Escape') {
      handleCancel()
    }
  }

  if (isEditing) {
    return (
      <div className="flex items-center gap-1">
        {type === 'select' ? (
          <select
            ref={inputRef as React.RefObject<HTMLSelectElement>}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={handleSave}
            onKeyDown={handleKeyDown}
            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-primary bg-background"
            disabled={isSaving}
          >
            <option value="">Select...</option>
            {options.map((opt) => (
              <option key={opt} value={opt}>{opt}</option>
            ))}
          </select>
        ) : (
          <input
            ref={inputRef as React.RefObject<HTMLInputElement>}
            type={type}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onBlur={handleSave}
            onKeyDown={handleKeyDown}
            className="w-full px-2 py-1 text-sm border rounded focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isSaving}
          />
        )}
        <button
          onClick={handleSave}
          className="p-1 text-green-600 hover:bg-green-100 rounded"
          disabled={isSaving}
        >
          <Check className="h-3 w-3" />
        </button>
        <button
          onClick={handleCancel}
          className="p-1 text-red-600 hover:bg-red-100 rounded"
          disabled={isSaving}
        >
          <X className="h-3 w-3" />
        </button>
      </div>
    )
  }

  return (
    <div
      onDoubleClick={handleDoubleClick}
      className={`cursor-pointer hover:bg-muted/50 px-1 py-0.5 rounded ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
      title={disabled ? 'Read-only' : 'Double-click to edit'}
    >
      {value || <span className="text-muted-foreground">-</span>}
    </div>
  )
}
