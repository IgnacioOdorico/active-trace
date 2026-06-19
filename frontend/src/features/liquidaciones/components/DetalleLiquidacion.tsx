import type { Liquidacion } from '../types'

interface Props {
  liquidacion: Liquidacion
  onClose: () => void
}

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

export default function DetalleLiquidacion({ liquidacion, onClose }: Props) {
  const plusTotal = liquidacion.monto_total - liquidacion.monto_base

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">
        <div className="mb-4 flex items-start justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">{liquidacion.docente_nombre}</h2>
            <p className="text-sm text-gray-500">
              {liquidacion.rol} — Período {liquidacion.periodo}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
            aria-label="Cerrar"
          >
            ✕
          </button>
        </div>

        <div className="space-y-3">
          <div className="flex justify-between border-b border-gray-100 pb-2">
            <span className="text-sm text-gray-600">Monto base</span>
            <span className="text-sm font-medium text-gray-900">
              {formatARS(liquidacion.monto_base)}
            </span>
          </div>

          {liquidacion.plus_detalle.length > 0 && (
            <div className="space-y-1">
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">Plus salarial</p>
              {liquidacion.plus_detalle.map((p) => (
                <div key={p.grupo} className="flex justify-between">
                  <span className="text-sm text-gray-600">Plus {p.grupo}</span>
                  <span className="text-sm text-gray-700">{formatARS(p.monto)}</span>
                </div>
              ))}
              <div className="flex justify-between border-t border-gray-100 pt-1">
                <span className="text-sm text-gray-600">Subtotal plus</span>
                <span className="text-sm font-medium text-gray-700">{formatARS(plusTotal)}</span>
              </div>
            </div>
          )}

          <div className="flex justify-between rounded-lg bg-blue-50 px-3 py-2">
            <span className="text-sm font-semibold text-blue-900">Total</span>
            <span className="text-sm font-bold text-blue-900">
              {formatARS(liquidacion.monto_total)}
            </span>
          </div>

          <div className="flex gap-2 pt-1">
            {liquidacion.es_nexo && (
              <span className="rounded bg-purple-100 px-2 py-0.5 text-xs text-purple-700">NEXO</span>
            )}
            {liquidacion.excluido_por_factura && (
              <span className="rounded bg-yellow-100 px-2 py-0.5 text-xs text-yellow-700">
                Facturante
              </span>
            )}
          </div>
        </div>

        <div className="mt-4 flex justify-end">
          <button
            onClick={onClose}
            className="rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  )
}
