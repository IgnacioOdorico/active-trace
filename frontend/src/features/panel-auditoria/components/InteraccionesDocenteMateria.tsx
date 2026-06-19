import { useInteraccionesPorDocenteMateria } from '../hooks/usePanelAuditoriaApi'
import type { PanelFilters } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'

interface Props {
  filters: PanelFilters
}

export default function InteraccionesDocenteMateria({ filters }: Props) {
  const { data, isLoading } = useInteraccionesPorDocenteMateria(filters)

  if (isLoading) {
    return <div className="h-32 animate-pulse rounded neo-latex-border bg-surface-container" />
  }

  if (!data || data.length === 0) {
    return (
      <p className="py-6 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border">
        Sin datos de interacciones para el rango seleccionado.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
      <table className="min-w-full divide-y divide-outline-variant">
        <thead className="bg-surface">
          <tr>
            <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Docente</th>
            <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Materia</th>
            <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Total</th>
            <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Por tipo</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
          {data.map((item) => (
            <tr key={`${item.docente_id}-${item.materia_id}`} className="hover:bg-surface-container transition-colors">
              <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{item.docente_nombre}</td>
              <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{item.materia_nombre}</td>
              <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface">{item.total_acciones}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {Object.entries(item.acciones_por_tipo ?? {}).map(([tipo, count]) => (
                    <Badge key={tipo} variant="neutral">
                      {tipo}: {count}
                    </Badge>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
