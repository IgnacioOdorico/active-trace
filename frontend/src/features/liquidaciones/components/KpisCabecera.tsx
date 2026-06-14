import { useKpisPeriodo } from '../hooks/useLiquidacionesApi'

interface Props {
  periodo: string | undefined
}

function KpiCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-white p-4 shadow-sm">
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-2xl font-bold text-gray-900">{value}</p>
    </div>
  )
}

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

export default function KpisCabecera({ periodo }: Props) {
  const { data, isLoading } = useKpisPeriodo(periodo)

  if (!periodo) return null

  if (isLoading) {
    return (
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-20 animate-pulse rounded-lg bg-gray-200" />
        ))}
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
      <KpiCard label="Total sin factura" value={formatARS(data.total_general + data.total_nexo)} />
      <KpiCard label="Total general" value={formatARS(data.total_general)} />
      <KpiCard label="Total NEXO" value={formatARS(data.total_nexo)} />
      <KpiCard
        label="Facturas pendientes"
        value={formatARS(data.total_facturas_pendientes)}
      />
      <KpiCard
        label="Facturas abonadas"
        value={formatARS(data.total_facturas_abonadas)}
      />
      <KpiCard label="Docentes generales" value={String(data.cantidad_general)} />
      <KpiCard label="Docentes NEXO" value={String(data.cantidad_nexo)} />
      <KpiCard label="Docentes facturantes" value={String(data.cantidad_facturantes)} />
    </div>
  )
}
