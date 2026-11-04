import { useEffect, useRef, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Loader2, AlertCircle } from 'lucide-react'
import { useTablePreferencesSync, loadStoredWidths } from '@/hooks/useTablePreferencesSync'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

export interface AdminColumn<T> {
  key: string
  header: string
  width?: string
  render?: (row: T) => React.ReactNode
  accessor?: (row: T) => React.ReactNode
}

interface AdminTableProps<T> {
  data: T[]
  columns: AdminColumn<T>[]
  loading?: boolean
  error?: string | null
  emptyMessage?: string
  rowKey: (row: T) => string | number
  onRowClick?: (row: T) => void
  actions?: (row: T) => React.ReactNode
  /** Enable column resizing via drag (default: true) */
  resizable?: boolean
  /** Minimum column width in px (default 60) */
  minColumnWidth?: number
  /**
   * If provided, column widths are persisted to localStorage under this key.
   * Use a stable, unique value per table (e.g. 'admin.users.cols').
   */
  storageKey?: string
}

const DEFAULT_COL_WIDTH = 180
const ACTIONS_COL_WIDTH = 120

function parseInitialWidth(w?: string): number {
  if (!w) return DEFAULT_COL_WIDTH
  const m = /^(\d+(?:\.\d+)?)px$/.exec(w.trim())
  if (m) return Math.round(parseFloat(m[1]))
  const n = parseFloat(w)
  return isNaN(n) ? DEFAULT_COL_WIDTH : Math.round(n)
}

export function AdminTable<T>({
  data,
  columns,
  loading,
  error,
  emptyMessage,
  rowKey,
  onRowClick,
  actions,
  resizable = true,
  minColumnWidth = 60,
  storageKey,
}: AdminTableProps<T>) {
  const { t } = useTranslation()
  const { save: syncSave } = useTablePreferencesSync()
  const effectiveEmptyMessage = emptyMessage ?? t('table.noData')
  // Per-column widths (px). Initialised from column.width when first seen,
  // overridden by any value previously persisted in localStorage.
  const [widths, setWidths] = useState<Record<string, number>>(() => {
    const init: Record<string, number> = {}
    for (const c of columns) init[c.key] = parseInitialWidth(c.width)
    if (actions) init.__actions__ = ACTIONS_COL_WIDTH
    const stored = loadStoredWidths(storageKey)
    return stored ? { ...init, ...stored } : init
  })

  // Re-sync when the set of columns changes (new key appears)
  useEffect(() => {
    setWidths((prev) => {
      const next = { ...prev }
      let changed = false
      for (const c of columns) {
        if (next[c.key] === undefined) {
          next[c.key] = parseInitialWidth(c.width)
          changed = true
        }
      }
      if (actions && next.__actions__ === undefined) {
        next.__actions__ = ACTIONS_COL_WIDTH
        changed = true
      }
      return changed ? next : prev
    })
  }, [columns, actions])

  // Persist widths whenever they change (localStorage + debounced server sync)
  useEffect(() => {
    if (!storageKey) return
    syncSave(storageKey, widths)
  }, [widths, storageKey, syncSave])

  const draggingRef = useRef<{
    key: string
    startX: number
    startWidth: number
  } | null>(null)

  const startResize = (key: string) => (e: React.MouseEvent) => {
    if (!resizable) return
    e.preventDefault()
    e.stopPropagation()
    draggingRef.current = {
      key,
      startX: e.clientX,
      startWidth: widths[key] ?? DEFAULT_COL_WIDTH,
    }
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'

    const onMove = (ev: MouseEvent) => {
      const d = draggingRef.current
      if (!d) return
      const delta = ev.clientX - d.startX
      const w = Math.max(minColumnWidth, d.startWidth + delta)
      setWidths((prev) => ({ ...prev, [d.key]: w }))
    }
    const onUp = () => {
      draggingRef.current = null
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
      window.removeEventListener('mousemove', onMove)
      window.removeEventListener('mouseup', onUp)
    }
    window.addEventListener('mousemove', onMove)
    window.addEventListener('mouseup', onUp)
  }
  if (loading) {
    return (
      <div className="flex h-40 items-center justify-center text-muted-foreground">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" />
        {t('table.loading')}
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 text-destructive">
        <AlertCircle className="h-6 w-6" />
        <span className="text-sm">{error}</span>
      </div>
    )
  }

  if (!data.length) {
    return (
      <div className="flex h-40 items-center justify-center rounded-md border border-dashed text-sm text-muted-foreground">
        {effectiveEmptyMessage}
      </div>
    )
  }

  return (
    <Table style={{ tableLayout: 'fixed' }}>
      <colgroup>
        {columns.map((c) => (
          <col key={c.key} style={{ width: `${widths[c.key] ?? DEFAULT_COL_WIDTH}px` }} />
        ))}
        {actions && (
          <col style={{ width: `${widths.__actions__ ?? ACTIONS_COL_WIDTH}px` }} />
        )}
      </colgroup>
      <TableHeader>
        <TableRow>
          {columns.map((c) => (
            <TableHead key={c.key} className="relative select-none">
              <span className="block truncate pr-2">{c.header}</span>
              {resizable && (
                <span
                  role="separator"
                  aria-orientation="vertical"
                  onMouseDown={startResize(c.key)}
                  onClick={(e) => e.stopPropagation()}
                  onDoubleClick={() =>
                    setWidths((prev) => ({
                      ...prev,
                      [c.key]: parseInitialWidth(c.width),
                    }))
                  }
                  className="absolute right-0 top-0 z-10 h-full w-1.5 cursor-col-resize bg-transparent hover:bg-primary/40 active:bg-primary/60"
                  title={t('table.resetColumnWidth')}
                />
              )}
            </TableHead>
          ))}
          {actions && (
            <TableHead className="relative select-none text-right">
              <span className="block truncate">{t('common.actions')}</span>
              {resizable && (
                <span
                  role="separator"
                  aria-orientation="vertical"
                  onMouseDown={startResize('__actions__')}
                  onClick={(e) => e.stopPropagation()}
                  onDoubleClick={() =>
                    setWidths((prev) => ({ ...prev, __actions__: ACTIONS_COL_WIDTH }))
                  }
                  className="absolute right-0 top-0 z-10 h-full w-1.5 cursor-col-resize bg-transparent hover:bg-primary/40 active:bg-primary/60"
                  title={t('table.resetColumnWidth')}
                />
              )}
            </TableHead>
          )}
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((row) => (
          <TableRow
            key={rowKey(row)}
            onClick={onRowClick ? () => onRowClick(row) : undefined}
            className={onRowClick ? 'cursor-pointer' : undefined}
          >
            {columns.map((c) => (
              <TableCell key={c.key} className="truncate">
                {c.render
                  ? c.render(row)
                  : c.accessor
                    ? c.accessor(row)
                    : ((row as unknown as Record<string, unknown>)[c.key] as React.ReactNode) ?? '—'}
              </TableCell>
            ))}
            {actions && (
              <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                <div className="flex justify-end gap-1">{actions(row)}</div>
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
