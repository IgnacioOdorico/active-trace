import { useState } from 'react'
import { useFacturas, useAbonarFactura } from '../hooks/useFacturasApi'
import type { EstadoFactura, FacturasFilters } from '../types'
import { Input } from '../../../shared/components/ui/Input'
import { Badge } from '../../../shared/components/ui/Badge'
import { Button } from '../../../shared/components/ui/Button'

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
      <div className="flex flex-wrap gap-4 rounded neo-latex-border bg-surface-container-lowest p-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps uppercase text-on-surface-variant">Período</label>
          <Input
            type="month"
            value={filters.periodo ?? ''}
            onChange={(e) => setFilters((f) => ({ ...f, periodo: e.target.value || undefined }))}
          />
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</label>
          <select
            className="neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
        <p className="rounded neo-latex-border bg-warning-container p-3 font-body-md text-on-warning-container">{abonarError}</p>
      )}

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="h-12 animate-pulse rounded neo-latex-border bg-surface-container" />
          ))}
        </div>
      )}

      {!isLoading && (!data || data.length === 0) && (
        <p className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
          No hay facturas para los filtros seleccionados.
        </p>
      )}

      {!isLoading && data && data.length > 0 && (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Período</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Detalle</th>
                <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Tamaño</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Cargada</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
                {puedeAbonar && (
                  <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Acción</th>
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {data.map((f) => (
                <tr key={f.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-mono-data text-mono-data font-medium text-on-surface">{f.periodo}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{f.detalle}</td>
                  <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface-variant">{f.tamano_kb} KB</td>
                  <td className="px-4 py-3 text-center font-mono-data text-mono-data text-on-surface-variant">
                    {new Date(f.cargada_at).toLocaleDateString('es-AR')}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Badge
                      variant={f.estado === 'Abonada' ? 'success' : 'warning'}
                    >
                      {f.estado}
                    </Badge>
                  </td>
                  {puedeAbonar && (
                    <td className="px-4 py-3 text-center">
                      {f.estado === 'Pendiente' && (
                        <Button
                          onClick={() => handleAbonar(f.id)}
                          disabled={abonando}
                          variant="ghost"
                          className="text-success hover:bg-success-container hover:text-on-success-container"
                        >
                          Marcar abonada
                        </Button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
