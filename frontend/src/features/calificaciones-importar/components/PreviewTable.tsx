import type { ActividadDetectada } from '../types'

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
  const allSelected = actividades.every((a) => selectedIds.includes(a.id))
  const someSelected = selectedIds.length > 0 && !allSelected

  function handleSelectAll() {
    if (allSelected) {
      onSelectionChange([])
    } else {
      onSelectionChange(actividades.map((a) => a.id))
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
      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-600">
          {materiaNombre} &mdash; {totalFilas} filas detectadas
        </p>
      </div>

      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="w-12 px-4 py-3 text-left">
                <input
                  type="checkbox"
                  checked={allSelected}
                  ref={(el) => {
                    if (el) el.indeterminate = someSelected
                  }}
                  onChange={handleSelectAll}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  aria-label="Seleccionar todo"
                />
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Actividad
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Tipo
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                Columnas
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {actividades.map((actividad) => (
              <tr key={actividad.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(actividad.id)}
                    onChange={() => handleToggle(actividad.id)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    aria-label={`Seleccionar ${actividad.nombre}`}
                  />
                </td>
                <td className="px-4 py-3 text-sm font-medium text-gray-900">
                  {actividad.nombre}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                      actividad.tipo === 'numerica'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-purple-100 text-purple-800'
                    }`}
                  >
                    {actividad.tipo === 'numerica' ? 'Numérica' : 'Textual'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">
                  {actividad.columnas.join(', ')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
