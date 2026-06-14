import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  FechasAcademicasResponse,
  FechasFilters,
  CrearFechaAcademicaRequest,
  EditarFechaAcademicaRequest,
} from '../types'

function buildParams(filters: Record<string, string | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') params.set(key, value)
  }
  return params.toString()
}

export function useFechasAcademicas(filters: FechasFilters = {}) {
  return useQuery({
    queryKey: ['fechas-academicas', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<FechasAcademicasResponse>(
        `/api/fechas-academicas${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useCrearFechaAcademica() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CrearFechaAcademicaRequest) => {
      const { data } = await apiClient.post('/api/fechas-academicas', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fechas-academicas'] })
    },
  })
}

export function useEditarFechaAcademica() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: EditarFechaAcademicaRequest }) => {
      const { data } = await apiClient.patch(`/api/fechas-academicas/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fechas-academicas'] })
    },
  })
}
