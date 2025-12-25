import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  flexRender,
  type ColumnDef,
  type SortingState,
  type ColumnFiltersState,
} from '@tanstack/react-table'
import { 
  ChevronUp, 
  ChevronDown, 
  Search, 
  Plus, 
  RefreshCw,
  Filter,
  Download,
  Edit,
  Trash2,
  Eye
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { engineeringApi, type Tag } from '@/lib/api'
import { useHierarchy } from '@/components/hierarchy'

export function InstrumentsPage() {
  const navigate = useNavigate()
  const { selectedProject, selectedClient, selectedSite, selectedPlant } = useHierarchy()
  
  const [data, setData] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [sorting, setSorting] = useState<SortingState>([])
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([])
  const [globalFilter, setGlobalFilter] = useState('')
  const [rowSelection, setRowSelection] = useState({})

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      // Build query params based on hierarchy selection
      const params: Record<string, number> = {}
      if (selectedPlant) {
        params.plant = selectedPlant.id
      } else if (selectedSite) {
        params.site = selectedSite.id
      } else if (selectedClient) {
        params.client = selectedClient.id
      } else if (selectedProject) {
        params.project = selectedProject.id
      }
      
      const response = await engineeringApi.tags.list(params)
      setData(response.results)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data')
    } finally {
      setLoading(false)
    }
  }

  // Refetch when hierarchy selection changes
  useEffect(() => {
    fetchData()
  }, [selectedProject, selectedClient, selectedSite, selectedPlant])

  const columns = useMemo<ColumnDef<Tag>[]>(
    () => [
      {
        id: 'select',
        header: ({ table }) => (
          <input
            type="checkbox"
            checked={table.getIsAllRowsSelected()}
            onChange={table.getToggleAllRowsSelectedHandler()}
            className="rounded border-gray-300"
          />
        ),
        cell: ({ row }) => (
          <input
            type="checkbox"
            checked={row.getIsSelected()}
            onChange={row.getToggleSelectedHandler()}
            className="rounded border-gray-300"
          />
        ),
        size: 40,
      },
      {
        accessorKey: 'tag_number',
        header: 'Tag Number',
        cell: ({ row }) => (
          <button
            onClick={() => navigate(`/instruments/${row.original.id}`)}
            className="font-mono font-medium text-blue-600 hover:text-blue-800 hover:underline"
          >
            {row.getValue('tag_number')}
          </button>
        ),
      },
      {
        accessorKey: 'service',
        header: 'Service',
        cell: ({ row }) => (
          <span className="text-sm">{row.getValue('service') || '-'}</span>
        ),
      },
      {
        accessorKey: 'status',
        header: 'Status',
        cell: ({ row }) => {
          const status = row.getValue('status') as string
          const statusColors: Record<string, string> = {
            ACTIVE: 'bg-green-100 text-green-800',
            INACTIVE: 'bg-gray-100 text-gray-800',
            PENDING: 'bg-yellow-100 text-yellow-800',
            UNDER_REVIEW: 'bg-blue-100 text-blue-800',
            DELETED: 'bg-red-100 text-red-800',
          }
          return (
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[status] || 'bg-gray-100'}`}>
              {status}
            </span>
          )
        },
      },
      {
        accessorKey: 'revision',
        header: 'Rev',
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground">
            R{row.getValue('revision')}
          </span>
        ),
        size: 60,
      },
      {
        accessorKey: 'description',
        header: 'Description',
        cell: ({ row }) => (
          <span className="text-sm text-muted-foreground truncate max-w-[200px] block">
            {row.getValue('description') || '-'}
          </span>
        ),
      },
      {
        accessorKey: 'updated_at',
        header: 'Last Updated',
        cell: ({ row }) => {
          const date = new Date(row.getValue('updated_at'))
          return (
            <span className="text-sm text-muted-foreground">
              {date.toLocaleDateString()}
            </span>
          )
        },
      },
      {
        id: 'actions',
        header: '',
        cell: ({ row }) => (
          <div className="flex items-center gap-1">
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-8 w-8" 
              title="View"
              onClick={() => navigate(`/instruments/${row.original.id}`)}
            >
              <Eye className="h-4 w-4" />
            </Button>
            <Button 
              variant="ghost" 
              size="icon" 
              className="h-8 w-8" 
              title="Edit"
              onClick={() => navigate(`/instruments/${row.original.id}`)}
            >
              <Edit className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500" title="Delete">
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ),
        size: 120,
      },
    ],
    []
  )

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
      columnFilters,
      globalFilter,
      rowSelection,
    },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    onRowSelectionChange: setRowSelection,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    enableRowSelection: true,
  })

  const selectedCount = Object.keys(rowSelection).length

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div>
          <h1 className="text-2xl font-bold">Instrument Index</h1>
          <p className="text-sm text-muted-foreground">
            Manage instrument tags and specifications
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={fetchData}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Tag
          </Button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-4 p-4 border-b bg-muted/30">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search tags..."
            value={globalFilter}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <Button variant="outline" size="sm">
          <Filter className="h-4 w-4 mr-2" />
          Filters
        </Button>
        {selectedCount > 0 && (
          <div className="flex items-center gap-2 ml-auto">
            <span className="text-sm text-muted-foreground">
              {selectedCount} selected
            </span>
            <Button variant="outline" size="sm">
              Bulk Edit
            </Button>
            <Button variant="outline" size="sm" className="text-red-500">
              Delete Selected
            </Button>
          </div>
        )}
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        {error ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-red-500 mb-2">{error}</p>
              <Button variant="outline" onClick={fetchData}>
                Try Again
              </Button>
            </div>
          </div>
        ) : loading ? (
          <div className="flex items-center justify-center h-full">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : data.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mb-4">
              <Search className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium mb-2">No instruments found</h3>
            <p className="text-muted-foreground mb-4">
              Get started by creating your first instrument tag.
            </p>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Tag
            </Button>
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-muted/50 sticky top-0">
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
              {table.getRowModel().rows.map((row) => (
                <tr
                  key={row.id}
                  className="border-b hover:bg-muted/30 transition-colors"
                >
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-3">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Pagination */}
      {data.length > 0 && (
        <div className="flex items-center justify-between p-4 border-t bg-muted/30">
          <div className="text-sm text-muted-foreground">
            Showing {table.getState().pagination.pageIndex * table.getState().pagination.pageSize + 1} to{' '}
            {Math.min(
              (table.getState().pagination.pageIndex + 1) * table.getState().pagination.pageSize,
              data.length
            )}{' '}
            of {data.length} results
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              Previous
            </Button>
            <div className="flex items-center gap-1">
              {Array.from({ length: table.getPageCount() }, (_, i) => (
                <Button
                  key={i}
                  variant={table.getState().pagination.pageIndex === i ? 'default' : 'outline'}
                  size="sm"
                  className="w-8"
                  onClick={() => table.setPageIndex(i)}
                >
                  {i + 1}
                </Button>
              )).slice(0, 5)}
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
