import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  EncuentrosInstanciasResponse,
  EncuentrosFilters,
  GuardiasResponse,
  GuardiasFilters,
  RegistrarGuardiaRequest,
  EditarGuardiaRequest,
} from '../types'

function buildParams(filters: Record<string, string | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') params.set(key, value)
  }
  return params.toString()
}

export function useEncuentrosInstancias(filters: EncuentrosFilters = {}) {
  return useQuery({
    queryKey: ['encuentros-instancias', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<EncuentrosInstanciasResponse>(
        `/api/encuentros/instancias${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useGuardias(filters: GuardiasFilters = {}) {
  return useQuery({
    queryKey: ['guardias', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<GuardiasResponse>(
        `/api/guardias${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useRegistrarGuardia() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: RegistrarGuardiaRequest) => {
      const { data } = await apiClient.post('/api/guardias', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guardias'] })
    },
  })
}

export function useEditarGuardia() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: EditarGuardiaRequest }) => {
      const { data } = await apiClient.patch(`/api/guardias/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['guardias'] })
    },
  })
}

export function useExportarGuardias() {
  return useMutation({
    mutationFn: async () => {
      const response = await apiClient.get('/api/guardias/exportar', {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'guardias.xlsx')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    },
  })
}
