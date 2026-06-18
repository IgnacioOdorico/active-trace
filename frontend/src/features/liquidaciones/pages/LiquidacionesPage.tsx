import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import { useLiquidaciones, useExportarPlanilla, useCalcularLiquidacion } from '../hooks/useLiquidacionesApi'
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
  const puedeCalcular = perms.includes('*:*') || perms.includes('liquidaciones:calcular')

  const [filters, setFilters] = useState<LiquidacionesFilters>({})
  const [detalle, setDetalle] = useState<Liquidacion | null>(null)
  const [cierre, setCierre] = useState<Liquidacion | null>(null)
  const [tab, setTab] = useState<'periodo' | 'historial'>('periodo')
  const [calcularMensaje, setCalcularMensaje] = useState<
    { tipo: 'ok' | 'error'; texto: string } | null
  >(null)

  const { data, isLoading, isError } = useLiquidaciones(filters)
  const exportarMutation = useExportarPlanilla()
  const calcularMutation = useCalcularLiquidacion()

  function handleCalcular() {
    if (!filters.cohorte_id || !filters.periodo) return
    setCalcularMensaje(null)
    calcularMutation.mutate(
      { cohorte_id: filters.cohorte_id, periodo: filters.periodo },
      {
        onSuccess: (data) => {
          setCalcularMensaje({
            tipo: 'ok',
            texto: `Se calcularon ${data.total} liquidaciones para el período ${filters.periodo}.`,
          })
        },
        onError: (err: unknown) => {
          const status = (err as { response?: { status?: number } })?.response?.status
          if (status === 409) {
            setCalcularMensaje({
              tipo: 'error',
              texto: 'Este período ya está cerrado para esta cohorte y no se puede recalcular.',
            })
          } else {
            setCalcularMensaje({
              tipo: 'error',
              texto: 'Ocurrió un error al calcular la liquidación. Intente nuevamente.',
            })
          }
        },
      },
    )
  }

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
        <div className="flex gap-2">
          {puedeCalcular && (
            <button
              disabled={!filters.cohorte_id || !filters.periodo || calcularMutation.isPending}
              title={
                !filters.cohorte_id || !filters.periodo
                  ? 'Seleccioná una cohorte y un período para calcular'
                  : undefined
              }
              onClick={handleCalcular}
              className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-300 disabled:text-gray-500"
            >
              {calcularMutation.isPending ? 'Calculando...' : 'Calcular liquidación'}
            </button>
          )}
          <button
            disabled={!filters.periodo || exportarMutation.isPending}
            title={!filters.periodo ? 'Seleccioná un período para exportar' : undefined}
            onClick={() =>
              filters.periodo &&
              exportarMutation.mutate({ periodo: filters.periodo, cohorte_id: filters.cohorte_id })
            }
            className="rounded-md border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:text-gray-400 disabled:hover:bg-transparent"
          >
            {exportarMutation.isPending ? 'Exportando...' : 'Exportar planilla'}
          </button>
        </div>
      </div>

      {calcularMensaje && (
        <p
          className={`rounded-lg p-3 text-sm ${
            calcularMensaje.tipo === 'ok'
              ? 'bg-green-50 text-green-700'
              : 'bg-yellow-50 text-yellow-700'
          }`}
        >
          {calcularMensaje.texto}
        </p>
      )}

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
