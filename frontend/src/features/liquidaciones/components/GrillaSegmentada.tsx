import type { Liquidacion } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'
import { Button } from '../../../shared/components/ui/Button'

interface Props {
  items: Liquidacion[]
  onVerDetalle: (liquidacion: Liquidacion) => void
}

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

interface SegmentoProps {
  titulo: string
  items: Liquidacion[]
  informativo?: boolean
  onVerDetalle: (liq: Liquidacion) => void
}

function FilaLiquidacion({
  liq,
  onVerDetalle,
}: {
  liq: Liquidacion
  onVerDetalle: (liq: Liquidacion) => void
}) {
  return (
    <tr className="hover:bg-surface-container transition-colors">
      <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{liq.docente_nombre}</td>
      <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{liq.rol}</td>
      <td className="px-4 py-3 text-center font-body-md text-body-md text-on-surface-variant">{liq.comisiones.length}</td>
      <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface-variant">{formatARS(liq.monto_base)}</td>
      <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface-variant">
        {formatARS(liq.monto_plus)}
      </td>
      <td className="px-4 py-3 text-right font-mono-data text-mono-data font-medium text-on-surface">
        {formatARS(liq.total)}
      </td>
      <td className="px-4 py-3 text-center">
        <Badge variant={liq.estado === 'Cerrada' ? 'neutral' : 'success'}>
          {liq.estado}
        </Badge>
      </td>
      <td className="px-4 py-3 text-center">
        <Button
          onClick={() => onVerDetalle(liq)}
          variant="ghost"
          size="sm"
        >
          Ver detalle
        </Button>
      </td>
    </tr>
  )
}

function Segmento({ titulo, items, informativo, onVerDetalle }: SegmentoProps) {
  if (items.length === 0) return null
  return (
    <div className="mb-8 last:mb-0">
      <div className="mb-3 flex items-center gap-3">
        <h3 className="font-label-caps text-label-caps uppercase text-on-surface">{titulo}</h3>
        {informativo && (
          <Badge variant="warning">
            Informativo — excluido del total
          </Badge>
        )}
        <span className="font-body-md text-on-surface-variant">({items.length} docentes)</span>
      </div>
      <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
        <table className="min-w-full divide-y divide-outline-variant">
          <thead className="bg-surface">
            <tr>
              <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Docente</th>
              <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Rol</th>
              <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Comisiones</th>
              <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Base</th>
              <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Plus</th>
              <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Total</th>
              <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
              <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Detalle</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
            {items.map((liq) => (
              <FilaLiquidacion key={liq.id} liq={liq} onVerDetalle={onVerDetalle} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default function GrillaSegmentada({ items, onVerDetalle }: Props) {
  const general = items.filter((l) => !l.es_nexo && !l.excluido_por_factura)
  const nexo = items.filter((l) => l.es_nexo)
  const facturantes = items.filter((l) => l.excluido_por_factura)

  if (items.length === 0) {
    return (
      <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
        Sin liquidaciones para el período seleccionado.
      </div>
    )
  }

  return (
    <div>
      <Segmento titulo="General" items={general} onVerDetalle={onVerDetalle} />
      <Segmento titulo="NEXO" items={nexo} onVerDetalle={onVerDetalle} />
      <Segmento titulo="Facturantes" items={facturantes} informativo onVerDetalle={onVerDetalle} />
    </div>
  )
}
