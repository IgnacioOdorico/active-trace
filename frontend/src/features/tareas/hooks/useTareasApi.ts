import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  TareasResponse,
  ComentariosResponse,
  CrearTareaRequest,
  CambiarEstadoRequest,
  AgregarComentarioRequest,
  TareasAdminFilters,
  TareaEstado,
} from '../types'

function buildParams(filters: Record<string, string | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') params.set(key, value)
  }
  return params.toString()
}

export function useMisTareas() {
  return useQuery({
    queryKey: ['tareas-mias'],
    queryFn: async () => {
      const { data } = await apiClient.get<TareasResponse>('/api/tareas/mias')
      return data
    },
  })
}

export function useTareasAdmin(filters: TareasAdminFilters = {}) {
  return useQuery({
    queryKey: ['tareas-admin', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<TareasResponse>(
        `/api/tareas${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useCrearTarea() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CrearTareaRequest) => {
      const { data } = await apiClient.post('/api/tareas', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tareas-admin'] })
      queryClient.invalidateQueries({ queryKey: ['tareas-mias'] })
    },
  })
}

export function useCambiarEstadoTarea() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: CambiarEstadoRequest }) => {
      const { data } = await apiClient.patch(`/api/tareas/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tareas-admin'] })
      queryClient.invalidateQueries({ queryKey: ['tareas-mias'] })
    },
  })
}

export function useComentarios(tareaId: string | null) {
  return useQuery({
    queryKey: ['tareas-comentarios', tareaId],
    queryFn: async () => {
      const { data } = await apiClient.get<ComentariosResponse>(
        `/api/tareas/${tareaId}/comentarios`,
      )
      return data
    },
    enabled: !!tareaId,
  })
}

export function useAgregarComentario(tareaId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: AgregarComentarioRequest) => {
      const { data } = await apiClient.post(
        `/api/tareas/${tareaId}/comentarios`,
        payload,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tareas-comentarios', tareaId] })
    },
  })
}

export const ESTADOS_WORKFLOW: TareaEstado[] = [
  'Pendiente',
  'En progreso',
  'Resuelta',
  'Cancelada',
]
