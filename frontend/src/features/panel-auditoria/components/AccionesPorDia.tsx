import { useAccionesPorDia } from '../hooks/usePanelAuditoriaApi'
import type { PanelFilters } from '../types'

interface Props {
  filters: PanelFilters
}

export default function AccionesPorDia({ filters }: Props) {
  const { data, isLoading } = useAccionesPorDia(filters)

  if (isLoading) {
    return <div className="h-32 animate-pulse rounded neo-latex-border bg-surface-container" />
  }

  if (!data || data.length === 0) {
    return (
      <p className="py-6 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border">
        Sin acciones registradas en el rango seleccionado.
      </p>
    )
  }

  const maxTotal = Math.max(...data.map((d) => d.total), 1)

  return (
    <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
      <table className="min-w-full divide-y divide-outline-variant">
        <thead className="bg-surface">
          <tr>
            <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Fecha</th>
            <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Acciones</th>
            <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Volumen</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
          {data.map((item) => (
            <tr key={item.fecha} className="hover:bg-surface-container transition-colors">
              <td className="px-4 py-3 font-body-md text-body-md text-on-surface">
                {new Date(item.fecha).toLocaleDateString('es-AR')}
              </td>
              <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface">
                {item.total}
              </td>
              <td className="px-4 py-3">
                <div className="h-2 w-full max-w-[200px] rounded-full bg-surface-container-highest overflow-hidden">
                  <div
                    className="h-full rounded-full bg-primary"
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
