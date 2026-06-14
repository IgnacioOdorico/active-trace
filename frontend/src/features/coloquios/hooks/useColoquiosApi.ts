import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  ColoquioMetricas,
  ConvocatoriasResponse,
  CrearConvocatoriaRequest,
  EditarConvocatoriaRequest,
  CerrarConvocatoriaResponse,
  ImportarAlumnosRequest,
  ImportarAlumnosResponse,
} from '../types'

export function useMetricas() {
  return useQuery({
    queryKey: ['coloquios-metricas'],
    queryFn: async () => {
      const { data } = await apiClient.get<ColoquioMetricas>('/api/coloquios/metricas')
      return data
    },
  })
}

export function useConvocatorias() {
  return useQuery({
    queryKey: ['coloquios-convocatorias'],
    queryFn: async () => {
      const { data } = await apiClient.get<ConvocatoriasResponse>('/api/coloquios')
      return data
    },
  })
}

export function useCrearConvocatoria() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CrearConvocatoriaRequest) => {
      const { data } = await apiClient.post('/api/coloquios', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coloquios-convocatorias'] })
      queryClient.invalidateQueries({ queryKey: ['coloquios-metricas'] })
    },
  })
}

export function useEditarConvocatoria() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      id,
      payload,
    }: {
      id: string
      payload: EditarConvocatoriaRequest
    }) => {
      const { data } = await apiClient.patch(`/api/coloquios/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coloquios-convocatorias'] })
    },
  })
}

export function useCerrarConvocatoria() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.patch<CerrarConvocatoriaResponse>(
        `/api/coloquios/${id}/cerrar`,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coloquios-convocatorias'] })
      queryClient.invalidateQueries({ queryKey: ['coloquios-metricas'] })
    },
  })
}

export function useImportarAlumnos() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: ImportarAlumnosRequest }) => {
      const { data } = await apiClient.post<ImportarAlumnosResponse>(
        `/api/coloquios/${id}/alumnos`,
        payload,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['coloquios-convocatorias'] })
      queryClient.invalidateQueries({ queryKey: ['coloquios-metricas'] })
    },
  })
}
