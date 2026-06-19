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
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { hasPermission } from '../../../shared/utils/permissions'

export default function LiquidacionesPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeVer = hasPermission(perms, 'liquidaciones:ver')
  const puedeCerrar = hasPermission(perms, 'liquidaciones:cerrar')
  const puedeCalcular = hasPermission(perms, 'liquidaciones:calcular')

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
      <BentoCard>
        <div className="rounded bg-error-container p-6 text-center font-body-md text-on-error-container">
          Acceso denegado. No tenés el permiso <code>liquidaciones:ver</code>.
        </div>
      </BentoCard>
    )
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Liquidaciones</h1>
        <div className="flex gap-2">
          {puedeCalcular && (
            <Button
              disabled={!filters.cohorte_id || !filters.periodo || calcularMutation.isPending}
              title={
                !filters.cohorte_id || !filters.periodo
                  ? 'Seleccioná una cohorte y un período para calcular'
                  : undefined
              }
              onClick={handleCalcular}
              variant="primary"
            >
              {calcularMutation.isPending ? 'Calculando...' : 'Calcular liquidación'}
            </Button>
          )}
          <Button
            disabled={!filters.periodo || exportarMutation.isPending}
            title={!filters.periodo ? 'Seleccioná un período para exportar' : undefined}
            onClick={() =>
              filters.periodo &&
              exportarMutation.mutate({ periodo: filters.periodo, cohorte_id: filters.cohorte_id })
            }
            variant="ghost"
          >
            {exportarMutation.isPending ? 'Exportando...' : 'Exportar planilla'}
          </Button>
        </div>
      </div>

      {calcularMensaje && (
        <p
          className={`rounded neo-latex-border p-4 font-body-md ${
            calcularMensaje.tipo === 'ok'
              ? 'bg-[#d4edda] text-[#155724]'
              : 'bg-error-container text-on-error-container'
          }`}
        >
          {calcularMensaje.texto}
        </p>
      )}

      <div className="flex gap-2 mb-6">
        {(['periodo', 'historial'] as const).map((t) => (
          <Button
            key={t}
            onClick={() => setTab(t)}
            variant={tab === t ? 'primary' : 'ghost'}
          >
            {t === 'periodo' ? 'Período actual' : 'Historial'}
          </Button>
        ))}
      </div>

      <BentoCard>
        {tab === 'periodo' && (
          <div className="space-y-6">
            <FiltrosPeriodo filters={filters} onChange={setFilters} />
            <KpisCabecera periodo={filters.periodo} />

            {isError && (
              <p className="rounded bg-error-container p-4 font-body-md text-on-error-container">
                Error al cargar las liquidaciones.
              </p>
            )}

            {isLoading && (
              <div className="space-y-2">
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} className="h-10 animate-pulse rounded bg-surface-container" />
                ))}
              </div>
            )}

            {!isLoading && data && (
              <>
                {puedeCerrar && data.items.some((l) => l.estado === 'Abierta') && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {data.items
                      .filter((l) => l.estado === 'Abierta')
                      .map((l) => (
                        <Button
                          key={l.id}
                          onClick={() => setCierre(l)}
                          variant="danger"
                          size="sm"
                        >
                          Cerrar: {l.docente_nombre}
                        </Button>
                      ))}
                  </div>
                )}
                <GrillaSegmentada items={data.items} onVerDetalle={setDetalle} />
              </>
            )}
          </div>
        )}

        {tab === 'historial' && <HistorialLiquidaciones />}
      </BentoCard>

      {detalle && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
          <BentoCard className="w-full max-w-4xl shadow-xl max-h-[90vh] overflow-y-auto" title="Detalle Liquidación" action={
            <button
              onClick={() => setDetalle(null)}
              className="material-symbols-outlined text-outline hover:text-on-surface"
            >
              close
            </button>
          }>
            <DetalleLiquidacion liquidacion={detalle} onClose={() => setDetalle(null)} />
          </BentoCard>
        </div>
      )}

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
