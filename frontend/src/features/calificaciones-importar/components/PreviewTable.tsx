import type { ActividadDetectada } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'

interface PreviewTableProps {
  actividades: ActividadDetectada[]
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
  materiaNombre: string
  totalFilas: number
}

export default function PreviewTable({
  actividades,
  selectedIds,
  onSelectionChange,
  materiaNombre,
  totalFilas,
}: PreviewTableProps) {
  const allSelected = actividades.every((a) => selectedIds.includes(a.nombre))
  const someSelected = selectedIds.length > 0 && !allSelected

  function handleSelectAll() {
    if (allSelected) {
      onSelectionChange([])
    } else {
      onSelectionChange(actividades.map((a) => a.nombre))
    }
  }

  function handleToggle(id: string) {
    if (selectedIds.includes(id)) {
      onSelectionChange(selectedIds.filter((s) => s !== id))
    } else {
      onSelectionChange([...selectedIds, id])
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between px-2">
        <p className="font-body-md text-on-surface-variant">
          <span className="font-medium text-on-surface">{materiaNombre}</span> &mdash; {totalFilas} filas detectadas
        </p>
      </div>

      <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
        <table className="min-w-full divide-y divide-outline-variant">
          <thead className="bg-surface">
            <tr>
              <th className="w-12 px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) el.indeterminate = someSelected
                  }}
                  onChange={handleSelectAll}
                  className="rounded border-outline-variant text-primary focus:ring-primary bg-surface-container-lowest"
                  aria-label="Seleccionar todo"
                />
              </th>
              <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">
                Actividad
              </th>
              <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">
                Tipo
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
            {actividades.map((actividad) => (
              <tr key={actividad.nombre} className="hover:bg-surface-container transition-colors">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(actividad.nombre)}
                    onChange={() => handleToggle(actividad.nombre)}
                    className="rounded border-outline-variant text-primary focus:ring-primary bg-surface-container-lowest"
                    aria-label={`Seleccionar ${actividad.nombre}`}
                  />
                </td>
                <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">
                  {actividad.nombre}
                </td>
                <td className="px-4 py-3">
                  <Badge 
                    variant={actividad.tipo === 'numerica' ? 'info' : 'warning'}
                  >
                    {actividad.tipo === 'numerica' ? 'Numérica' : 'Textual'}
                  </Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
