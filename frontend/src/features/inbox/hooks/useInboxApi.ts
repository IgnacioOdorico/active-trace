import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { InboxResponse, HiloDetalle, Mensaje } from '../types'

export function useHilos(pagina: number = 1, pageSize: number = 20) {
  return useQuery({
    queryKey: ['inbox-hilos', pagina],
    queryFn: async () => {
      const { data } = await apiClient.get<InboxResponse>(
        `/api/inbox?pagina=${pagina}&page_size=${pageSize}`,
      )
      return data
    },
  })
}

export function useHilo(hiloId: string | null) {
  return useQuery({
    queryKey: ['inbox-hilo', hiloId],
    queryFn: async () => {
      const { data } = await apiClient.get<HiloDetalle>(`/api/inbox/${hiloId}`)
      return data
    },
    enabled: !!hiloId,
  })
}

export function useResponderHilo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      hiloId,
      cuerpo,
    }: {
      hiloId: string
      cuerpo: string
    }) => {
      const { data } = await apiClient.post<Mensaje>(`/api/inbox/${hiloId}/responder`, { cuerpo })
      return data
    },
    onSuccess: (_data, { hiloId }) => {
      queryClient.invalidateQueries({ queryKey: ['inbox-hilo', hiloId] })
      queryClient.invalidateQueries({ queryKey: ['inbox-hilos'] })
    },
  })
}
