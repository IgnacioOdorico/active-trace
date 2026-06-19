import { useState, useCallback } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useAuth } from '../../auth/hooks/useAuth'
import { useComunicacionesApi } from '../hooks/useComunicacionesApi'
import ComunicacionForm from '../components/ComunicacionForm'
import ComunicacionTracking from '../components/ComunicacionTracking'
import type { PreviewRequest, PreviewResponse, EnviarRequest, EnviarResponse } from '../types'
import { Button } from '../../../shared/components/ui/Button'

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
    <div className="mx-auto max-w-4xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Comunicaciones</h1>
      </div>

      <div className="flex gap-2 mb-6 border-b border-outline-variant pb-2">
        <Button
          onClick={() => setViewMode('form')}
          variant={viewMode === 'form' ? 'primary' : 'ghost'}
        >
          Redactar
        </Button>
        <Button
          onClick={() => setViewMode('tracking')}
          variant={viewMode === 'tracking' ? 'primary' : 'ghost'}
        >
          Tracking
        </Button>
      </div>

      <div>
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
          <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
            No hay lote seleccionado. Envíe una comunicación para ver su tracking o ingrese un ID de lote en la URL.
          </div>
        )}
      </div>
    </div>
  )
}
