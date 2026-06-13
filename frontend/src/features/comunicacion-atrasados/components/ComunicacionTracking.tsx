import { useState } from 'react'
import { useComunicacionesApi } from '../hooks/useComunicacionesApi'
import type { ComunicacionItem } from '../types'

function estadoColor(estado: string): string {
  switch (estado) {
    case 'Enviado':
      return 'bg-green-100 text-green-800'
    case 'Pendiente':
    case 'PendienteAprobacion':
      return 'bg-yellow-100 text-yellow-800'
    case 'Error':
      return 'bg-red-100 text-red-800'
    case 'Cancelado':
      return 'bg-gray-100 text-gray-800'
    default:
      return 'bg-gray-100 text-gray-800'
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

  const estadosDisponibles = data
    ? [...new Set(data.comunicaciones.map((c: ComunicacionItem) => c.estado))]
    : []

  const filtered = data
    ? statusFilter
      ? data.comunicaciones.filter((c: ComunicacionItem) => c.estado === statusFilter)
      : data.comunicaciones
    : []

  if (tracking.isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
        <p className="ml-3 text-sm text-gray-600">Cargando tracking...</p>
      </div>
    )
  }

  if (tracking.isError) {
    return (
      <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">
        Error al cargar el tracking del lote.
      </div>
    )
  }

  if (!data) return null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            Tracking de Lote
          </h2>
          <p className="text-sm text-gray-500">Lote ID: {data.lote_id}</p>
        </div>
        <span
          className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${estadoColor(data.estado_lote)}`}
        >
          {estadoLabel(data.estado_lote)}
        </span>
      </div>

      {data.requiere_aprobacion && (
        <div className="rounded-md bg-yellow-50 p-4">
          <p className="text-sm text-yellow-800">
            Este lote requiere aprobación antes de ser enviado. Estado actual: {estadoLabel(data.estado_lote)}
          </p>
          {canApprove && (
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                onClick={() => aprobarLote.mutate(loteId)}
                disabled={aprobarLote.isPending}
                className="rounded-md bg-green-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-700 disabled:opacity-50"
              >
                {aprobarLote.isPending ? 'Aprobando...' : 'Aprobar Lote'}
              </button>
              <button
                type="button"
                onClick={() => rechazarLote.mutate(loteId)}
                disabled={rechazarLote.isPending}
                className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                {rechazarLote.isPending ? 'Rechazando...' : 'Rechazar Lote'}
              </button>
            </div>
          )}
        </div>
      )}

      <div>
        <label htmlFor="statusFilter" className="block text-sm font-medium text-gray-700">
          Filtrar por estado
        </label>
        <select
          id="statusFilter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="mt-1 block w-full max-w-xs rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Todos</option>
          {estadosDisponibles.map((est: string) => (
            <option key={est} value={est}>{estadoLabel(est)}</option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto rounded-md border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Destinatario</th>
              <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Estado</th>
              <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Intentos</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Error</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Enviado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200 bg-white">
            {filtered.map((c: ComunicacionItem) => (
              <tr key={c.id}>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-900">{c.destinatario}</td>
                <td className="whitespace-nowrap px-4 py-3 text-center">
                  <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${estadoColor(c.estado)}`}>
                    {estadoLabel(c.estado)}
                  </span>
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-center text-sm text-gray-600">{c.intentos}</td>
                <td className="max-w-xs truncate px-4 py-3 text-sm text-gray-600">{c.error_msg || '-'}</td>
                <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{c.enviado_at || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-sm text-gray-500">{data.total} comunicación(es) en total</p>
    </div>
  )
}
