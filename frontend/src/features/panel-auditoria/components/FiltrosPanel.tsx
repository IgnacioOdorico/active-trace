import { useMaterias } from '../../academico/hooks/useMaterias'
import type { PanelFilters } from '../types'
import { Input } from '../../../shared/components/ui/Input'

interface Props {
  filters: PanelFilters
  onChange: (filters: PanelFilters) => void
}

export default function FiltrosPanel({ filters, onChange }: Props) {
  const { data: materias } = useMaterias()

  return (
    <div className="flex flex-wrap gap-4 rounded neo-latex-border bg-surface-container-lowest p-4">
      <div className="flex flex-col gap-1 w-[200px]">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Desde</label>
        <Input
          type="datetime-local"
          value={filters.desde ?? ''}
          onChange={(e) => onChange({ ...filters, desde: e.target.value || undefined })}
        />
      </div>
      <div className="flex flex-col gap-1 w-[200px]">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Hasta</label>
        <Input
          type="datetime-local"
          value={filters.hasta ?? ''}
          onChange={(e) => onChange({ ...filters, hasta: e.target.value || undefined })}
        />
      </div>
      <div className="flex flex-col gap-1 w-[200px]">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Materia</label>
        <select
          className="rounded neo-latex-border bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary w-full"
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
      <div className="flex flex-col gap-1 w-[240px]">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Tipo de acción</label>
        <Input
          type="text"
          placeholder="Ej: LIQUIDACION_CERRAR"
          value={filters.accion ?? ''}
          onChange={(e) => onChange({ ...filters, accion: e.target.value || undefined })}
        />
      </div>
    </div>
  )
}
