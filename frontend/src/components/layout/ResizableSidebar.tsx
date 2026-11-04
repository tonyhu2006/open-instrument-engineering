import { useCallback, useEffect, useRef, useState } from 'react'
import { Sidebar } from './Sidebar'

const STORAGE_KEY = 'oi.sidebarWidth'
const DEFAULT_WIDTH = 256
const MIN_WIDTH = 200
const MAX_WIDTH = 560

function clamp(value: number) {
  return Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, value))
}

function readInitialWidth(): number {
  if (typeof window === 'undefined') return DEFAULT_WIDTH
  const raw = window.localStorage.getItem(STORAGE_KEY)
  const parsed = raw ? Number(raw) : NaN
  return Number.isFinite(parsed) ? clamp(parsed) : DEFAULT_WIDTH
}

export function ResizableSidebar() {
  const [width, setWidth] = useState<number>(readInitialWidth)
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)

  // Persist width
  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, String(width))
  }, [width])

  // Global mouse handlers while dragging
  useEffect(() => {
    if (!isDragging) return

    const handleMove = (e: MouseEvent) => {
      const left = containerRef.current?.getBoundingClientRect().left ?? 0
      setWidth(clamp(e.clientX - left))
    }
    const handleUp = () => setIsDragging(false)

    // Prevent text selection / cursor flicker globally during drag
    const prevUserSelect = document.body.style.userSelect
    const prevCursor = document.body.style.cursor
    document.body.style.userSelect = 'none'
    document.body.style.cursor = 'col-resize'

    window.addEventListener('mousemove', handleMove)
    window.addEventListener('mouseup', handleUp)
    return () => {
      window.removeEventListener('mousemove', handleMove)
      window.removeEventListener('mouseup', handleUp)
      document.body.style.userSelect = prevUserSelect
      document.body.style.cursor = prevCursor
    }
  }, [isDragging])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDoubleClick = useCallback(() => {
    setWidth(DEFAULT_WIDTH)
  }, [])

  // Keyboard accessibility — left/right arrow keys when handle is focused
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    const step = e.shiftKey ? 32 : 8
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      setWidth((w) => clamp(w - step))
    } else if (e.key === 'ArrowRight') {
      e.preventDefault()
      setWidth((w) => clamp(w + step))
    } else if (e.key === 'Home') {
      e.preventDefault()
      setWidth(MIN_WIDTH)
    } else if (e.key === 'End') {
      e.preventDefault()
      setWidth(MAX_WIDTH)
    }
  }, [])

  return (
    <div
      ref={containerRef}
      className="relative flex shrink-0"
      style={{ width: `${width}px` }}
    >
      <div className="flex w-full overflow-hidden">
        <Sidebar />
      </div>

      {/* Drag handle — sits over the right border, slightly wider for grab area */}
      <div
        role="separator"
        aria-label="Resize sidebar"
        aria-orientation="vertical"
        aria-valuenow={width}
        aria-valuemin={MIN_WIDTH}
        aria-valuemax={MAX_WIDTH}
        tabIndex={0}
        onMouseDown={handleMouseDown}
        onDoubleClick={handleDoubleClick}
        onKeyDown={handleKeyDown}
        className={`group absolute top-0 right-0 h-full w-1.5 translate-x-1/2 cursor-col-resize select-none outline-none ${
          isDragging ? 'bg-primary/40' : 'bg-transparent hover:bg-primary/30'
        } focus-visible:bg-primary/50 transition-colors`}
        title="Drag to resize (double-click to reset, arrow keys to fine-tune)"
      >
        {/* Subtle visible indicator on hover */}
        <div
          className={`absolute inset-y-0 left-1/2 w-px -translate-x-1/2 ${
            isDragging
              ? 'bg-primary'
              : 'bg-border group-hover:bg-primary/60'
          } transition-colors`}
        />
      </div>
    </div>
  )
}
