import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { PerfilResponse, PerfilUpdate } from '../types'

export function usePerfil() {
  return useQuery({
    queryKey: ['perfil'],
    queryFn: async () => {
      const { data } = await apiClient.get<PerfilResponse>('/api/perfil')
      return data
    },
  })
}

export function useActualizarPerfil() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: PerfilUpdate) => {
      const { data } = await apiClient.put<PerfilResponse>('/api/perfil', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['perfil'] })
    },
  })
}
