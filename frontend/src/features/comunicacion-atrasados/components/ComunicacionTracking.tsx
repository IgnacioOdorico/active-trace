import { useState } from 'react'
import { useComunicacionesApi } from '../hooks/useComunicacionesApi'
import type { ComunicacionItem } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

function estadoVariant(estado: string): 'success' | 'warning' | 'error' | 'neutral' {
  switch (estado) {
    case 'Enviado':
      return 'success'
    case 'Pendiente':
    case 'PendienteAprobacion':
    case 'Enviando':
      return 'warning'
    case 'Error':
      return 'error'
    case 'Cancelado':
      return 'neutral'
    default:
      return 'neutral'
  }
}

function estadoLabel(estado: string): string {
  switch (estado) {
    case 'PendienteAprobacion':
      return 'Pendiente Aprobación'
    default:
      return estado
  }
}

interface Props {
  loteId: string
  canApprove: boolean
}

export default function ComunicacionTracking({ loteId, canApprove }: Props) {
  const { tracking, aprobarLote, rechazarLote } = useComunicacionesApi(loteId)
  const [statusFilter, setStatusFilter] = useState<string>('')

  const data = tracking.data
  const items = data?.items ?? []

  const estadosDisponibles = [...new Set(items.map((c: ComunicacionItem) => c.estado))]

  const filtered = statusFilter
    ? items.filter((c: ComunicacionItem) => c.estado === statusFilter)
    : items

  const requiereAprobacion = items.some((c) => c.estado === 'PendienteAprobacion')

  function derivarEstadoLote(): string {
    if (items.some((c) => c.estado === 'Error')) return 'Error'
    if (items.some((c) => c.estado === 'Enviando')) return 'Enviando'
    if (items.some((c) => c.estado === 'PendienteAprobacion')) return 'PendienteAprobacion'
    if (items.some((c) => c.estado === 'Pendiente')) return 'Pendiente'
    if (items.every((c) => c.estado === 'Enviado')) return 'Enviado'
    if (items.every((c) => c.estado === 'Cancelado')) return 'Cancelado'
    return 'Pendiente'
  }

  const estadoLote = data ? derivarEstadoLote() : ''

  if (tracking.isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
        <p className="ml-3 font-body-md text-on-surface-variant">Cargando tracking...</p>
      </div>
    )
  }

  if (tracking.isError) {
    return (
      <div className="rounded neo-latex-border bg-error-container p-4 font-body-md text-on-error-container">
        Error al cargar el tracking del lote.
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      <BentoCard>
        <div className="flex items-center justify-between border-b border-outline-variant pb-4 mb-4">
          <div>
            <h2 className="font-headline-sm text-headline-sm text-on-surface">
              Tracking de Lote
            </h2>
            <p className="font-mono-data text-mono-data text-on-surface-variant mt-1">Lote ID: {loteId}</p>
          </div>
          <Badge variant={estadoVariant(estadoLote)}>
            {estadoLabel(estadoLote)}
          </Badge>
        </div>

        {requiereAprobacion && (
          <div className="rounded neo-latex-border bg-[#F2C94C]/10 border-l-4 border-[#F2C94C] p-4 mb-6">
            <p className="font-body-md font-medium text-on-surface">
              Este lote requiere aprobación antes de ser enviado. Estado actual: <span className="font-bold">{estadoLabel(estadoLote)}</span>
            </p>
            {canApprove && (
              <div className="mt-4 flex gap-3">
                <Button
                  onClick={() => aprobarLote.mutate(loteId)}
                  disabled={aprobarLote.isPending}
                  variant="primary"
                >
                  {aprobarLote.isPending ? 'Aprobando...' : 'Aprobar Lote'}
                </Button>
                <Button
                  onClick={() => rechazarLote.mutate(loteId)}
                  disabled={rechazarLote.isPending}
                  variant="secondary"
                  className="!text-error hover:!bg-error/10 border-error/50"
                >
                  {rechazarLote.isPending ? 'Rechazando...' : 'Rechazar Lote'}
                </Button>
              </div>
            )}
          </div>
        )}

        <div className="mb-4">
          <label htmlFor="statusFilter" className="font-label-caps text-label-caps text-on-surface-variant uppercase mb-1 block">
            Filtrar por estado
          </label>
          <select
            id="statusFilter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="block w-full max-w-xs neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">Todos</option>
            {estadosDisponibles.map((est: string) => (
              <option key={est} value={est}>{estadoLabel(est)}</option>
            ))}
          </select>
        </div>

        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Destinatario</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Intentos</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Error</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Enviado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {filtered.map((c: ComunicacionItem) => (
                <tr key={c.id} className="hover:bg-surface-container transition-colors">
                  <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{c.destinatario}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-center">
                    <Badge variant={estadoVariant(c.estado)}>
                      {estadoLabel(c.estado)}
                    </Badge>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-center font-mono-data text-mono-data text-on-surface-variant">{c.intentos}</td>
                  <td className="max-w-xs truncate px-4 py-3 font-body-md text-body-md text-on-surface-variant">{c.error_msg || '-'}</td>
                  <td className="whitespace-nowrap px-4 py-3 font-mono-data text-mono-data text-on-surface-variant">{c.enviado_at || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 pt-4 border-t border-outline-variant flex justify-end">
          <p className="font-body-md text-on-surface-variant">
            <span className="font-mono-data font-bold text-on-surface">{data?.total ?? 0}</span> comunicación(es) en total
          </p>
        </div>
      </BentoCard>
    </div>
  )
}
