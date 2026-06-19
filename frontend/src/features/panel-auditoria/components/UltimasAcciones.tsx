import { useState } from 'react'
import { useUltimasAcciones } from '../hooks/usePanelAuditoriaApi'
import type { PanelFilters } from '../types'

interface Props {
  filters: PanelFilters
}

const MAX_OPTIONS = [50, 100, 200, 500]

export default function UltimasAcciones({ filters }: Props) {
  const [max, setMax] = useState(200)
  const { data, isLoading } = useUltimasAcciones(filters, max)

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700">Últimas acciones</h4>
        <div className="flex items-center gap-2">
          <label className="text-xs text-gray-500">Mostrar:</label>
          <select
            value={max}
            onChange={(e) => setMax(Number(e.target.value))}
            className="rounded-md border border-gray-300 px-2 py-1 text-xs focus:border-blue-500 focus:outline-none"
          >
            {MAX_OPTIONS.map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
      </div>

      {isLoading && <div className="h-32 animate-pulse rounded-lg bg-gray-200" />}

      {!isLoading && (!data || data.items.length === 0) && (
        <p className="py-6 text-center text-sm text-gray-500">
          Sin acciones en el rango seleccionado.
        </p>
      )}

      {!isLoading && data && data.items.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white text-xs">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-gray-500">Fecha/hora</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">Acción</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">Actor</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">Materia</th>
                <th className="px-3 py-2 text-right font-medium text-gray-500">Filas</th>
                <th className="px-3 py-2 text-left font-medium text-gray-500">IP</th>
              </tr>
            </thead>
            <tbody>
              {data.items.map((item) => (
                <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="px-3 py-2 text-gray-600">
                    {new Date(item.fecha_hora).toLocaleString('es-AR')}
                  </td>
                  <td className="px-3 py-2 font-medium text-gray-900">{item.accion}</td>
                  <td className="px-3 py-2 text-gray-600">{item.actor_nombre || item.actor_id.slice(0, 8) + '…'}</td>
                  <td className="px-3 py-2 text-gray-600">{item.materia_nombre || '—'}</td>
                  <td className="px-3 py-2 text-right text-gray-600">
                    {item.filas_afectadas ?? '—'}
                  </td>
                  <td className="px-3 py-2 text-gray-500">{item.ip ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
