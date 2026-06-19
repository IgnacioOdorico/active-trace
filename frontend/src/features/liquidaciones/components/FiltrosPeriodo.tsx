import type { LiquidacionesFilters } from '../types'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'

interface Props {
  filters: LiquidacionesFilters
  onChange: (filters: LiquidacionesFilters) => void
}

export default function FiltrosPeriodo({ filters, onChange }: Props) {
  const { data: cohortes } = useCohortes()

  return (
    <div className="flex flex-wrap gap-3 rounded-lg bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-1">
        <label htmlFor="liq-cohorte" className="text-xs font-medium text-gray-600">Cohorte</label>
        <select
          id="liq-cohorte"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          value={filters.cohorte_id ?? ''}
          onChange={(e) => onChange({ ...filters, cohorte_id: e.target.value || undefined })}
        >
          <option value="">Todas las cohortes</option>
          {cohortes?.map((c) => (
            <option key={c.id} value={c.id}>
              {c.nombre}
            </option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="liq-periodo" className="text-xs font-medium text-gray-600">Período (AAAA-MM)</label>
        <input
          id="liq-periodo"
          type="month"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          value={filters.periodo ?? ''}
          onChange={(e) => onChange({ ...filters, periodo: e.target.value || undefined })}
        />
      </div>
    </div>
  )
}
