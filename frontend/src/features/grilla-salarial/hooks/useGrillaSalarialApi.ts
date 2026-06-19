import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  SalarioBase,
  SalarioBaseCreate,
  SalarioBaseUpdate,
  SalarioPlus,
  SalarioPlusCreate,
  SalarioPlusUpdate,
} from '../types'

// --- Salario Base ---

export function useSalariosBase() {
  return useQuery({
    queryKey: ['salario-base'],
    queryFn: async () => {
      const { data } = await apiClient.get<SalarioBase[]>('/api/salario-base')
      return data
    },
  })
}

export function useCrearSalarioBase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: SalarioBaseCreate) => {
      const { data } = await apiClient.post<SalarioBase>('/api/salario-base', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salario-base'] })
    },
  })
}

export function useActualizarSalarioBase() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: SalarioBaseUpdate }) => {
      const { data } = await apiClient.put<SalarioBase>(`/api/salario-base/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salario-base'] })
    },
  })
}

// --- Salario Plus ---

export function useSalariosPlus() {
  return useQuery({
    queryKey: ['salario-plus'],
    queryFn: async () => {
      const { data } = await apiClient.get<SalarioPlus[]>('/api/salario-plus')
      return data
    },
  })
}

export function useCrearSalarioPlus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: SalarioPlusCreate) => {
      const { data } = await apiClient.post<SalarioPlus>('/api/salario-plus', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salario-plus'] })
    },
  })
}

export function useActualizarSalarioPlus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: SalarioPlusUpdate }) => {
      const { data } = await apiClient.put<SalarioPlus>(`/api/salario-plus/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['salario-plus'] })
    },
  })
}
