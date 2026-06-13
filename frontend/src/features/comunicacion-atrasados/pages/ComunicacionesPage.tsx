import { useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../../auth/hooks/useAuth'
import { useComunicacionesApi } from '../hooks/useComunicacionesApi'
import ComunicacionForm from '../components/ComunicacionForm'
import ComunicacionTracking from '../components/ComunicacionTracking'
import type { PreviewRequest, PreviewResponse, EnviarRequest, EnviarResponse } from '../types'

type ViewMode = 'form' | 'tracking'

export default function ComunicacionesPage() {
  const { user } = useAuth()
  const [searchParams, setSearchParams] = useSearchParams()

  const loteIdFromUrl = searchParams.get('lote_id')
  const initialMateriaId = searchParams.get('materia_id') ?? undefined
  const initialDestinatarioEmail = searchParams.get('destinatario_email') ?? undefined

  const [viewMode, setViewMode] = useState<ViewMode>(loteIdFromUrl ? 'tracking' : 'form')
  const [trackingLoteId, setTrackingLoteId] = useState<string | null>(loteIdFromUrl)

  const { preview, enviar } = useComunicacionesApi(trackingLoteId)

  const handlePreview = useCallback(
    async (params: PreviewRequest): Promise<PreviewResponse> => {
      const data = await preview.mutateAsync(params)
      return data
    },
    [preview],
  )

  const handleEnviar = useCallback(
    async (params: EnviarRequest): Promise<EnviarResponse> => {
      const data = await enviar.mutateAsync(params)
      setTrackingLoteId(data.lote_id)
      setViewMode('tracking')
      setSearchParams({ lote_id: data.lote_id })
      return data
    },
    [enviar, setSearchParams],
  )

  return (
    <div className="mx-auto max-w-4xl py-8">
      <h1 className="text-2xl font-bold text-gray-900">Comunicaciones</h1>

      <div className="mt-6 flex gap-4 border-b border-gray-200">
        <button
          type="button"
          onClick={() => setViewMode('form')}
          className={`pb-2 text-sm font-medium ${
            viewMode === 'form'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Redactar
        </button>
        <button
          type="button"
          onClick={() => setViewMode('tracking')}
          className={`pb-2 text-sm font-medium ${
            viewMode === 'tracking'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Tracking
        </button>
      </div>

      <div className="mt-6">
        {viewMode === 'form' && (
          <ComunicacionForm
            initialMateriaId={initialMateriaId}
            initialDestinatarioEmail={initialDestinatarioEmail}
            onPreview={handlePreview}
            onEnviar={handleEnviar}
          />
        )}

        {viewMode === 'tracking' && trackingLoteId && (
          <ComunicacionTracking
            loteId={trackingLoteId}
            canApprove={(user?.permissions.includes('*:*') || user?.permissions.includes('comunicacion:aprobar')) ?? false}
          />
        )}

        {viewMode === 'tracking' && !trackingLoteId && (
          <div className="rounded-md bg-blue-50 p-4 text-sm text-blue-800">
            No hay lote seleccionado. Envíe una comunicación para ver su tracking o ingrese un ID de lote en la URL.
          </div>
        )}
      </div>
    </div>
  )
}
