import { useState } from 'react'
import { useHistorialLiquidaciones } from '../hooks/useLiquidacionesApi'
import type { HistorialFilters, EstadoLiquidacion } from '../types'

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

export default function HistorialLiquidaciones() {
  const [filters, setFilters] = useState<HistorialFilters>({})
  const { data, isLoading } = useHistorialLiquidaciones(filters)

  return (
    <div>
      <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-gray-700">
        Historial de liquidaciones
      </h3>

      <div className="mb-4 flex flex-wrap gap-3 rounded-lg bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-600">Desde</label>
          <input
            type="month"
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            value={filters.desde ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, desde: e.target.value || undefined }))}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-600">Hasta</label>
          <input
            type="month"
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            value={filters.hasta ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, hasta: e.target.value || undefined }))}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-600">Estado</label>
          <select
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            value={filters.estado ?? ''}
            onChange={(e) =>
              setFilters((f) => ({
                ...f,
                estado: (e.target.value as EstadoLiquidacion) || undefined,
              }))
            }
          >
            <option value="">Todos</option>
            <option value="Abierta">Abierta</option>
            <option value="Cerrada">Cerrada</option>
          </select>
        </div>
      </div>

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-10 animate-pulse rounded bg-gray-200" />
          ))}
        </div>
      )}

      {!isLoading && data?.items.length === 0 && (
        <p className="py-6 text-center text-sm text-gray-500">Sin registros en el historial.</p>
      )}

      {!isLoading && data && data.items.length > 0 && (
        <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Período</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Docentes</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Monto total</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((item) => (
              <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium text-gray-900">{item.periodo}</td>
                <td className="px-4 py-2 text-center">
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      item.estado === 'Cerrada'
                        ? 'bg-gray-100 text-gray-600'
                        : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {item.estado}
                  </span>
                </td>
                <td className="px-4 py-2 text-right text-sm text-gray-600">{item.total_docentes}</td>
                <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">
                  {formatARS(item.monto_total)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
