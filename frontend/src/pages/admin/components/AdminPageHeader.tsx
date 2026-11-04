import { Plus, RefreshCw } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

interface AdminPageHeaderProps {
  title: string
  description?: string
  searchValue?: string
  onSearchChange?: (v: string) => void
  searchPlaceholder?: string
  onRefresh?: () => void
  onCreate?: () => void
  createLabel?: string
  canCreate?: boolean
  extraActions?: React.ReactNode
}

export function AdminPageHeader({
  title,
  description,
  searchValue,
  onSearchChange,
  searchPlaceholder,
  onRefresh,
  onCreate,
  createLabel,
  canCreate = true,
  extraActions,
}: AdminPageHeaderProps) {
  const { t } = useTranslation()
  const effectiveSearchPlaceholder = searchPlaceholder ?? t('common.searchPlaceholder')
  const effectiveCreateLabel = createLabel ?? t('common.new')
  return (
    <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      <div className="flex items-center gap-2">
        {onSearchChange && (
          <Input
            value={searchValue ?? ''}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={effectiveSearchPlaceholder}
            className="h-8 w-56"
          />
        )}
        {extraActions}
        {onRefresh && (
          <Button variant="outline" size="sm" onClick={onRefresh}>
            <RefreshCw className="h-4 w-4" />
          </Button>
        )}
        {onCreate && canCreate && (
          <Button size="sm" onClick={onCreate}>
            <Plus className="h-4 w-4" />
            {effectiveCreateLabel}
          </Button>
        )}
      </div>
    </div>
  )
}
