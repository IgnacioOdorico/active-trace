import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { Usuario, UsuarioListResponse, UsuarioCreate, UsuarioUpdate, UsuariosFilters } from '../types'

function buildParams(filters: Record<string, string | number | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, String(value))
    }
  }
  return params.toString()
}

export function useUsuarios(filters: UsuariosFilters = {}) {
  return useQuery({
    queryKey: ['usuarios', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | number | undefined>)
      const { data } = await apiClient.get<UsuarioListResponse>(
        `/api/admin/usuarios${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useCrearUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: UsuarioCreate) => {
      const { data } = await apiClient.post<Usuario>('/api/admin/usuarios', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
  })
}

export function useActualizarUsuario() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: UsuarioUpdate }) => {
      const { data } = await apiClient.patch<Usuario>(`/api/admin/usuarios/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
  })
}

export function useToggleUsuarioEstado() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, activo }: { id: string; activo: boolean }) => {
      const { data } = await apiClient.patch<Usuario>(`/api/admin/usuarios/${id}`, {
        estado: activo ? 'Activo' : 'Inactivo',
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuarios'] })
    },
  })
}
