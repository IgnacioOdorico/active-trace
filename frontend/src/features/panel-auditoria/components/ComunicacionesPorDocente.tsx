import { useComunicacionesPorDocente } from '../hooks/usePanelAuditoriaApi'
import type { PanelFilters } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'

interface Props {
  filters: PanelFilters
}

const ESTADOS = ['pendiente', 'enviando', 'enviado', 'fallido', 'cancelado'] as const

export default function ComunicacionesPorDocente({ filters }: Props) {
  const { data, isLoading } = useComunicacionesPorDocente(filters)

  if (isLoading) {
    return <div className="h-32 animate-pulse rounded neo-latex-border bg-surface-container" />
  }

  if (!data || data.length === 0) {
    return (
      <p className="py-6 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border">
        Sin datos de comunicaciones para el rango seleccionado.
      </p>
    )
  }

  return (
    <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
      <table className="min-w-full divide-y divide-outline-variant">
        <thead className="bg-surface">
          <tr>
            <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Docente</th>
            {ESTADOS.map((e) => (
              <th key={e} className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">
                {e}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
          {data.map((item) => (
            <tr key={item.docente_id} className="hover:bg-surface-container transition-colors">
              <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{item.docente_nombre}</td>
              {ESTADOS.map((estado) => {
                let badgeVariant: "neutral" | "primary" | "secondary" | "error" | "success" = "neutral"
                if (estado === 'pendiente') badgeVariant = 'secondary'
                if (estado === 'enviando') badgeVariant = 'primary'
                if (estado === 'enviado') badgeVariant = 'success'
                if (estado === 'fallido') badgeVariant = 'error'

                return (
                  <td key={estado} className="px-4 py-3 text-center">
                    {item[estado] > 0 && (
                      <Badge variant={badgeVariant}>
                        {item[estado]}
                      </Badge>
                    )}
                    {item[estado] === 0 && (
                      <span className="font-mono-data text-mono-data text-on-surface-variant/50">—</span>
                    )}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
