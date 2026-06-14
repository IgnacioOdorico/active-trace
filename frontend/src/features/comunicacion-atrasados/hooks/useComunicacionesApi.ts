import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { PreviewRequest, PreviewResponse, EnviarRequest, EnviarResponse, TrackingResponse } from '../types'

export function useComunicacionesApi(loteId: string | null) {
  const queryClient = useQueryClient()

  const preview = useMutation({
    mutationFn: async (params: PreviewRequest) => {
      const { data } = await apiClient.post<PreviewResponse>(
        '/api/comunicaciones/preview',
        params,
      )
      return data
    },
  })

  const enviar = useMutation({
    mutationFn: async (params: EnviarRequest) => {
      const { data } = await apiClient.post<EnviarResponse>(
        '/api/comunicaciones/enviar',
        params,
      )
      return data
    },
  })

  const tracking = useQuery({
    queryKey: ['comunicaciones-tracking', loteId],
    queryFn: async () => {
      const { data } = await apiClient.get<TrackingResponse>(
        `/api/comunicaciones?lote_id=${loteId}`,
      )
      return data
    },
    enabled: !!loteId,
  })

  const aprobarLote = useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post(
        `/api/comunicaciones/lote/${id}/aprobar`,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comunicaciones-tracking'] })
    },
  })

  const rechazarLote = useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post(
        `/api/comunicaciones/lote/${id}/rechazar`,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['comunicaciones-tracking'] })
    },
  })

  return { preview, enviar, tracking, aprobarLote, rechazarLote }
}
