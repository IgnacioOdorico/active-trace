import { useState } from 'react'
import { useFacturas, useAbonarFactura } from '../hooks/useFacturasApi'
import type { EstadoFactura, FacturasFilters } from '../types'

interface Props {
  puedeAbonar: boolean
}

export default function FacturasListado({ puedeAbonar }: Props) {
  const [filters, setFilters] = useState<FacturasFilters>({})
  const { data, isLoading } = useFacturas(filters)
  const { mutate: abonar, isPending: abonando } = useAbonarFactura()
  const [abonarError, setAbonarError] = useState<string | null>(null)

  function handleAbonar(id: string) {
    setAbonarError(null)
    abonar(id, {
      onError: (err: unknown) => {
        const status = (err as { response?: { status?: number } })?.response?.status
        if (status === 409) {
          setAbonarError('Esta factura ya estaba marcada como abonada.')
        } else {
          setAbonarError('Error al marcar la factura. Intente nuevamente.')
        }
      },
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-3 rounded-lg bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-gray-600">Período</label>
          <input
            type="month"
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            value={filters.periodo ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, periodo: e.target.value || undefined }))}
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
                estado: (e.target.value as EstadoFactura) || undefined,
              }))
            }
          >
            <option value="">Todos</option>
            <option value="Pendiente">Pendiente</option>
            <option value="Abonada">Abonada</option>
          </select>
        </div>
      </div>

      {abonarError && (
        <p className="rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">{abonarError}</p>
      )}

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-10 animate-pulse rounded bg-gray-200" />
          ))}
        </div>
      )}

      {!isLoading && (!data || data.length === 0) && (
        <p className="py-6 text-center text-sm text-gray-500">
          No hay facturas para los filtros seleccionados.
        </p>
      )}

      {!isLoading && data && data.length > 0 && (
        <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Período</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Detalle</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Tamaño</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Cargada</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
              {puedeAbonar && (
                <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Acción</th>
              )}
            </tr>
          </thead>
          <tbody>
            {data.map((f) => (
              <tr key={f.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium text-gray-900">{f.periodo}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{f.detalle}</td>
                <td className="px-4 py-2 text-right text-sm text-gray-500">{f.tamano_kb} KB</td>
                <td className="px-4 py-2 text-center text-sm text-gray-500">
                  {new Date(f.cargada_at).toLocaleDateString('es-AR')}
                </td>
                <td className="px-4 py-2 text-center">
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      f.estado === 'Abonada'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-yellow-100 text-yellow-700'
                    }`}
                  >
                    {f.estado}
                  </span>
                </td>
                {puedeAbonar && (
                  <td className="px-4 py-2 text-center">
                    {f.estado === 'Pendiente' && (
                      <button
                        onClick={() => handleAbonar(f.id)}
                        disabled={abonando}
                        className="rounded px-2 py-1 text-xs text-green-700 hover:bg-green-50 disabled:opacity-50"
                      >
                        Marcar abonada
                      </button>
                    )}
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
