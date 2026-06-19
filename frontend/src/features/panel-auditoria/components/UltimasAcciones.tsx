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
    <div className="space-y-4">
      <div className="flex items-center justify-between rounded neo-latex-border bg-surface-container-lowest p-4">
        <h4 className="font-headline-sm text-headline-sm text-on-surface">Últimas acciones</h4>
        <div className="flex items-center gap-2">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Mostrar:</label>
          <select
            value={max}
            onChange={(e) => setMax(Number(e.target.value))}
            className="rounded neo-latex-border bg-surface-container-lowest px-2 py-1 font-mono-data text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {MAX_OPTIONS.map((n) => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
      </div>

      {isLoading && <div className="h-32 animate-pulse rounded neo-latex-border bg-surface-container" />}

      {!isLoading && (!data || data.items.length === 0) && (
        <p className="py-6 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border">
          Sin acciones en el rango seleccionado.
        </p>
      )}

      {!isLoading && data && data.items.length > 0 && (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Fecha/hora</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Acción</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Actor</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Materia</th>
                <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Filas</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">IP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {data.items.map((item) => (
                <tr key={item.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-mono-data text-[12px] text-on-surface-variant">
                    {new Date(item.fecha_hora).toLocaleString('es-AR')}
                  </td>
                  <td className="px-4 py-3 font-mono-data text-[12px] font-semibold text-on-surface">{item.accion}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{item.actor_nombre || item.actor_id.slice(0, 8) + '…'}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{item.materia_nombre || '—'}</td>
                  <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface">
                    {item.filas_afectadas ?? '—'}
                  </td>
                  <td className="px-4 py-3 font-mono-data text-[12px] text-on-surface-variant/50">{item.ip ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
