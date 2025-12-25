import { useRef } from 'react'
import { useVirtualizer } from '@tanstack/react-virtual'
import {
  flexRender,
  type Table,
  type Row,
} from '@tanstack/react-table'
import { ChevronUp, ChevronDown } from 'lucide-react'

interface VirtualTableProps<T> {
  table: Table<T>
  onRowClick?: (row: Row<T>) => void
  rowHeight?: number
}

export function VirtualTable<T>({
  table,
  onRowClick,
  rowHeight = 48,
}: VirtualTableProps<T>) {
  const tableContainerRef = useRef<HTMLDivElement>(null)

  const { rows } = table.getRowModel()

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => rowHeight,
    overscan: 10,
  })

  const virtualRows = rowVirtualizer.getVirtualItems()
  const totalSize = rowVirtualizer.getTotalSize()

  const paddingTop = virtualRows.length > 0 ? virtualRows[0]?.start || 0 : 0
  const paddingBottom =
    virtualRows.length > 0
      ? totalSize - (virtualRows[virtualRows.length - 1]?.end || 0)
      : 0

  return (
    <div
      ref={tableContainerRef}
      className="flex-1 overflow-auto"
      style={{ contain: 'strict' }}
    >
      <table className="w-full">
        <thead className="bg-muted/50 sticky top-0 z-10">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th
                  key={header.id}
                  className="px-4 py-3 text-left text-sm font-medium text-muted-foreground"
                  style={{ width: header.getSize() }}
                >
                  {header.isPlaceholder ? null : (
                    <div
                      className={`flex items-center gap-2 ${
                        header.column.getCanSort() ? 'cursor-pointer select-none' : ''
                      }`}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {flexRender(header.column.columnDef.header, header.getContext())}
                      {header.column.getIsSorted() === 'asc' && <ChevronUp className="h-4 w-4" />}
                      {header.column.getIsSorted() === 'desc' && <ChevronDown className="h-4 w-4" />}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody>
          {paddingTop > 0 && (
            <tr>
              <td style={{ height: `${paddingTop}px` }} />
            </tr>
          )}
          {virtualRows.map((virtualRow) => {
            const row = rows[virtualRow.index]
            return (
              <tr
                key={row.id}
                className={`border-b hover:bg-muted/30 transition-colors ${
                  onRowClick ? 'cursor-pointer' : ''
                }`}
                style={{ height: `${rowHeight}px` }}
                onClick={() => onRowClick?.(row)}
              >
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="px-4 py-3">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            )
          })}
          {paddingBottom > 0 && (
            <tr>
              <td style={{ height: `${paddingBottom}px` }} />
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
