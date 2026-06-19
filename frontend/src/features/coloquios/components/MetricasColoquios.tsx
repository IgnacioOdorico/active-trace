import { useMetricas } from '../hooks/useColoquiosApi'
import { BentoCard } from '../../../shared/components/ui/BentoCard'

interface MetricaCardProps {
  label: string
  value: number | undefined
}

function MetricaCard({ label, value }: MetricaCardProps) {
  return (
    <BentoCard className="flex flex-col justify-center items-center text-center p-6 h-full">
      <p className="font-label-caps text-label-caps text-on-surface-variant uppercase tracking-wider mb-2">{label}</p>
      <p className="font-mono-data text-headline-lg font-bold text-on-surface">
        {value !== undefined ? value : '—'}
      </p>
    </BentoCard>
  )
}

export default function MetricasColoquios() {
  const { data, isLoading, isError } = useMetricas()

  if (isLoading) {
    return <div className="py-4 font-body-md text-on-surface-variant">Cargando métricas...</div>
  }

  if (isError) {
    return <div className="py-4 font-body-md text-error">Error al cargar métricas.</div>
  }

  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <MetricaCard label="Alumnos cargados" value={data?.total_alumnos_convocados} />
      <MetricaCard label="Instancias activas" value={data?.total_instancias_activas} />
      <MetricaCard label="Reservas activas" value={data?.total_reservas_activas} />
      <MetricaCard label="Notas registradas" value={data?.total_notas_registradas} />
    </div>
  )
}
