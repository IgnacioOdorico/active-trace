import type { Liquidacion } from '../types'

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
    <tr className="border-b border-gray-100 hover:bg-gray-50">
      <td className="px-4 py-2 text-sm text-gray-900">{liq.docente_nombre}</td>
      <td className="px-4 py-2 text-sm text-gray-600">{liq.rol}</td>
      <td className="px-4 py-2 text-center text-sm text-gray-600">{liq.comisiones}</td>
      <td className="px-4 py-2 text-right text-sm text-gray-700">{formatARS(liq.monto_base)}</td>
      <td className="px-4 py-2 text-right text-sm text-gray-700">
        {formatARS(liq.monto_total - liq.monto_base)}
      </td>
      <td className="px-4 py-2 text-right text-sm font-medium text-gray-900">
        {formatARS(liq.monto_total)}
      </td>
      <td className="px-4 py-2 text-center text-sm">
        <span
          className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
            liq.estado === 'Cerrada'
              ? 'bg-gray-100 text-gray-600'
              : 'bg-green-100 text-green-700'
          }`}
        >
          {liq.estado}
        </span>
      </td>
      <td className="px-4 py-2 text-center">
        <button
          onClick={() => onVerDetalle(liq)}
          className="rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-50"
        >
          Ver detalle
        </button>
      </td>
    </tr>
  )
}

function Segmento({ titulo, items, informativo, onVerDetalle }: SegmentoProps) {
  if (items.length === 0) return null
  return (
    <div className="mb-6">
      <div className="mb-2 flex items-center gap-2">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700">{titulo}</h3>
        {informativo && (
          <span className="rounded bg-yellow-50 px-2 py-0.5 text-xs text-yellow-700">
            Informativo — excluido del total
          </span>
        )}
        <span className="text-xs text-gray-400">({items.length} docentes)</span>
      </div>
      <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Docente</th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Rol</th>
            <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Comisiones</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Base</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Plus</th>
            <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Total</th>
            <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
            <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Detalle</th>
          </tr>
        </thead>
        <tbody>
          {items.map((liq) => (
            <FilaLiquidacion key={liq.id} liq={liq} onVerDetalle={onVerDetalle} />
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function GrillaSegmentada({ items, onVerDetalle }: Props) {
  const general = items.filter((l) => !l.es_nexo && !l.excluido_por_factura)
  const nexo = items.filter((l) => l.es_nexo)
  const facturantes = items.filter((l) => l.excluido_por_factura)

  if (items.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-gray-500">
        Sin liquidaciones para el período seleccionado.
      </p>
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
