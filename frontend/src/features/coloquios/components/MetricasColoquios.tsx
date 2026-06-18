import { useMetricas } from '../hooks/useColoquiosApi'

interface MetricaCardProps {
  label: string
  value: number | undefined
}

function MetricaCard({ label, value }: MetricaCardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-sm font-medium text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900">
        {value !== undefined ? value : '—'}
      </p>
    </div>
  )
}

export default function MetricasColoquios() {
  const { data, isLoading, isError } = useMetricas()

  if (isLoading) {
    return <div className="py-4 text-sm text-gray-500">Cargando métricas...</div>
  }

  if (isError) {
    return <div className="py-4 text-sm text-red-600">Error al cargar métricas.</div>
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
