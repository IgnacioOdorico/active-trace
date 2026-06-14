import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { ProgramasResponse } from '../types'

export function useProgramas() {
  return useQuery({
    queryKey: ['programas'],
    queryFn: async () => {
      const { data } = await apiClient.get<ProgramasResponse>('/api/programas')
      return data
    },
  })
}

export function useSubirPrograma() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (formData: FormData) => {
      // El archivo se sube como multipart/form-data
      const { data } = await apiClient.post('/api/programas', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['programas'] })
    },
  })
}
