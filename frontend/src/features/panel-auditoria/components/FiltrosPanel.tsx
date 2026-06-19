import { useMaterias } from '../../academico/hooks/useMaterias'
import type { PanelFilters } from '../types'

interface Props {
  filters: PanelFilters
  onChange: (filters: PanelFilters) => void
}

export default function FiltrosPanel({ filters, onChange }: Props) {
  const { data: materias } = useMaterias()

  return (
    <div className="flex flex-wrap gap-3 rounded-lg bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600">Desde</label>
        <input
          type="datetime-local"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          value={filters.desde ?? ''}
          onChange={(e) => onChange({ ...filters, desde: e.target.value || undefined })}
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600">Hasta</label>
        <input
          type="datetime-local"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          value={filters.hasta ?? ''}
          onChange={(e) => onChange({ ...filters, hasta: e.target.value || undefined })}
        />
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600">Materia</label>
        <select
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          value={filters.materia_id ?? ''}
          onChange={(e) => onChange({ ...filters, materia_id: e.target.value || undefined })}
        >
          <option value="">Todas</option>
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-gray-600">Tipo de acción</label>
        <input
          type="text"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          placeholder="Ej: LIQUIDACION_CERRAR"
          value={filters.accion ?? ''}
          onChange={(e) => onChange({ ...filters, accion: e.target.value || undefined })}
        />
      </div>
    </div>
  )
}
