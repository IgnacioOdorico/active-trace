import { useInteraccionesPorDocenteMateria } from '../hooks/usePanelAuditoriaApi'
import type { PanelFilters } from '../types'

interface Props {
  filters: PanelFilters
}

export default function InteraccionesDocenteMateria({ filters }: Props) {
  const { data, isLoading } = useInteraccionesPorDocenteMateria(filters)

  if (isLoading) {
    return <div className="h-32 animate-pulse rounded-lg bg-gray-200" />
  }

  if (!data || data.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-gray-500">
        Sin datos de interacciones para el rango seleccionado.
      </p>
    )
  }

  return (
    <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Docente</th>
          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Materia</th>
          <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Total</th>
          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Por tipo</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr key={`${item.docente_id}-${item.materia_id}`} className="border-b border-gray-100 hover:bg-gray-50">
            <td className="px-4 py-2 text-sm font-medium text-gray-900">{item.docente_nombre}</td>
            <td className="px-4 py-2 text-sm text-gray-700">{item.materia_nombre}</td>
            <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">{item.total_acciones}</td>
            <td className="px-4 py-2">
              <div className="flex flex-wrap gap-1">
                {Object.entries(item.acciones_por_tipo ?? {}).map(([tipo, count]) => (
                  <span key={tipo} className="rounded bg-gray-100 px-1.5 py-0.5 text-xs text-gray-600">
                    {tipo}: {count}
                  </span>
                ))}
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
