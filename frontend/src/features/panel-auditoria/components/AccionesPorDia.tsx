import { useAccionesPorDia } from '../hooks/usePanelAuditoriaApi'
import type { PanelFilters } from '../types'

interface Props {
  filters: PanelFilters
}

export default function AccionesPorDia({ filters }: Props) {
  const { data, isLoading } = useAccionesPorDia(filters)

  if (isLoading) {
    return <div className="h-32 animate-pulse rounded-lg bg-gray-200" />
  }

  if (!data || data.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-gray-500">
        Sin acciones registradas en el rango seleccionado.
      </p>
    )
  }

  const maxTotal = Math.max(...data.map((d) => d.total), 1)

  return (
    <div className="overflow-x-auto">
      <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Fecha</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Acciones</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Volumen</th>
          </tr>
        </thead>
        <tbody>
          {data.map((item) => (
            <tr key={item.fecha} className="border-b border-gray-100">
              <td className="px-4 py-2 text-sm text-gray-700">
                {new Date(item.fecha).toLocaleDateString('es-AR')}
              </td>
              <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                {item.total}
              </td>
              <td className="px-4 py-2">
                <div className="h-3 rounded-full bg-gray-100">
                  <div
                    className="h-3 rounded-full bg-blue-500"
                    style={{ width: `${(item.total / maxTotal) * 100}%` }}
                  />
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
