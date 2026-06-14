import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import { useLiquidaciones } from '../hooks/useLiquidacionesApi'
import FiltrosPeriodo from '../components/FiltrosPeriodo'
import KpisCabecera from '../components/KpisCabecera'
import GrillaSegmentada from '../components/GrillaSegmentada'
import DetalleLiquidacion from '../components/DetalleLiquidacion'
import CierreConfirmacion from '../components/CierreConfirmacion'
import HistorialLiquidaciones from '../components/HistorialLiquidaciones'
import type { Liquidacion, LiquidacionesFilters } from '../types'

export default function LiquidacionesPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeVer = perms.includes('*:*') || perms.includes('liquidaciones:ver')
  const puedeCerrar = perms.includes('*:*') || perms.includes('liquidaciones:cerrar')

  const [filters, setFilters] = useState<LiquidacionesFilters>({})
  const [detalle, setDetalle] = useState<Liquidacion | null>(null)
  const [cierre, setCierre] = useState<Liquidacion | null>(null)
  const [tab, setTab] = useState<'periodo' | 'historial'>('periodo')

  const { data, isLoading, isError } = useLiquidaciones(filters)

  if (!puedeVer) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-sm text-red-700">
        Acceso denegado. No tenés el permiso <code>liquidaciones:ver</code>.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Liquidaciones</h1>
        <button
          disabled
          title="Export no disponible aún"
          className="cursor-not-allowed rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-400"
        >
          Exportar planilla
        </button>
      </div>

      <div className="flex gap-2 border-b border-gray-200">
        {(['periodo', 'historial'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium capitalize ${
              tab === t
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {t === 'periodo' ? 'Período actual' : 'Historial'}
          </button>
        ))}
      </div>

      {tab === 'periodo' && (
        <>
          <FiltrosPeriodo filters={filters} onChange={setFilters} />
          <KpisCabecera periodo={filters.periodo} />

          {isError && (
            <p className="rounded-lg bg-red-50 p-4 text-sm text-red-700">
              Error al cargar las liquidaciones.
            </p>
          )}

          {isLoading && (
            <div className="space-y-2">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-10 animate-pulse rounded bg-gray-200" />
              ))}
            </div>
          )}

          {!isLoading && data && (
            <>
              {puedeCerrar && data.items.some((l) => l.estado === 'Abierta') && (
                <div className="flex flex-wrap gap-2">
                  {data.items
                    .filter((l) => l.estado === 'Abierta')
                    .map((l) => (
                      <button
                        key={l.id}
                        onClick={() => setCierre(l)}
                        className="rounded-md bg-red-50 px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-red-100"
                      >
                        Cerrar: {l.docente_nombre}
                      </button>
                    ))}
                </div>
              )}
              <GrillaSegmentada items={data.items} onVerDetalle={setDetalle} />
            </>
          )}
        </>
      )}

      {tab === 'historial' && <HistorialLiquidaciones />}

      {detalle && <DetalleLiquidacion liquidacion={detalle} onClose={() => setDetalle(null)} />}

      {cierre && (
        <CierreConfirmacion
          liquidacion={cierre}
          onClosed={() => setCierre(null)}
          onCancel={() => setCierre(null)}
        />
      )}
    </div>
  )
}
