import type { ActividadDetectada } from '../types'

interface PreviewTableProps {
  actividades: ActividadDetectada[]
  selectedIds: string[]
  onSelectionChange: (ids: string[]) => void
  materiaNombre: string
  totalFilas: number
  preview?: Record<string, string>[]
}

export default function PreviewTable({
  actividades,
  selectedIds,
  onSelectionChange,
  materiaNombre,
  totalFilas,
  preview,
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

  function handleToggle(nombre: string) {
    if (selectedIds.includes(nombre)) {
      onSelectionChange(selectedIds.filter((s) => s !== nombre))
    } else {
      onSelectionChange([...selectedIds, nombre])
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
              {preview && preview.length > 0 && (
                <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">
                  Valor de muestra
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {actividades.map((actividad) => (
              <tr key={actividad.nombre} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedIds.includes(actividad.nombre)}
                    onChange={() => handleToggle(actividad.nombre)}
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
                {preview && preview.length > 0 && (
                  <td className="px-4 py-3 text-sm text-gray-500">
                    {preview[0][actividad.nombre] ?? '-'}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
