import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  AvisosGestionResponse,
  AvisosUsuarioResponse,
  CrearAvisoRequest,
  EditarAvisoRequest,
} from '../types'

export function useAvisosGestion() {
  return useQuery({
    queryKey: ['avisos-gestion'],
    queryFn: async () => {
      const { data } = await apiClient.get<AvisosGestionResponse>('/api/avisos/gestion')
      return data
    },
  })
}

export function useAvisosUsuario() {
  return useQuery({
    queryKey: ['avisos-usuario'],
    queryFn: async () => {
      const { data } = await apiClient.get<AvisosUsuarioResponse>('/api/avisos')
      return data
    },
  })
}

export function useCrearAviso() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CrearAvisoRequest) => {
      const { data } = await apiClient.post('/api/avisos', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos-gestion'] })
      queryClient.invalidateQueries({ queryKey: ['avisos-usuario'] })
    },
  })
}

export function useEditarAviso() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: EditarAvisoRequest }) => {
      const { data } = await apiClient.patch(`/api/avisos/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos-gestion'] })
      queryClient.invalidateQueries({ queryKey: ['avisos-usuario'] })
    },
  })
}

export function useEliminarAviso() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      await apiClient.delete(`/api/avisos/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos-gestion'] })
      queryClient.invalidateQueries({ queryKey: ['avisos-usuario'] })
    },
  })
}

export function useAckAviso() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post(`/api/avisos/${id}/ack`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['avisos-usuario'] })
    },
  })
}
