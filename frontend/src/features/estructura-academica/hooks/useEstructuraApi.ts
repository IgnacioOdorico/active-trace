import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  Carrera,
  CarreraCreate,
  CarreraUpdate,
  Cohorte,
  CohorteCreate,
  CohorteUpdate,
  Materia,
  MateriaCreate,
  MateriaUpdate,
} from '../types'

// =====================
// Carreras
// =====================

export function useCarreras() {
  return useQuery({
    queryKey: ['carreras'],
    queryFn: async () => {
      const { data } = await apiClient.get<Carrera[]>('/api/v1/admin/carreras')
      return data
    },
  })
}

export function useCrearCarrera() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CarreraCreate) => {
      const { data } = await apiClient.post<Carrera>('/api/v1/admin/carreras', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['carreras'] })
    },
  })
}

export function useActualizarCarrera() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: CarreraUpdate }) => {
      const { data } = await apiClient.put<Carrera>(`/api/v1/admin/carreras/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['carreras'] })
    },
  })
}

// =====================
// Cohortes (catálogo reutilizable por liquidaciones)
// =====================

export function useCohortes(carreraId?: string) {
  return useQuery({
    queryKey: ['cohortes', carreraId],
    queryFn: async () => {
      const qs = carreraId ? `?carrera_id=${carreraId}` : ''
      const { data } = await apiClient.get<Cohorte[]>(`/api/v1/admin/cohortes${qs}`)
      return data
    },
  })
}

export function useCrearCohorte() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: CohorteCreate) => {
      const { data } = await apiClient.post<Cohorte>('/api/v1/admin/cohortes', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cohortes'] })
    },
  })
}

export function useActualizarCohorte() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: CohorteUpdate }) => {
      const { data } = await apiClient.put<Cohorte>(`/api/v1/admin/cohortes/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cohortes'] })
    },
  })
}

// =====================
// Materias (ABM admin — reutilizar useMaterias de features/academico para lectura compartida)
// =====================

export function useMateriasAdmin() {
  return useQuery({
    queryKey: ['materias-admin'],
    queryFn: async () => {
      const { data } = await apiClient.get<Materia[]>('/api/v1/admin/materias')
      return data
    },
  })
}

export function useCrearMateria() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: MateriaCreate) => {
      const { data } = await apiClient.post<Materia>('/api/v1/admin/materias', payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['materias-admin'] })
      queryClient.invalidateQueries({ queryKey: ['materias'] }) // shared read hook
    },
  })
}

export function useActualizarMateria() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: MateriaUpdate }) => {
      const { data } = await apiClient.put<Materia>(`/api/v1/admin/materias/${id}`, payload)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['materias-admin'] })
      queryClient.invalidateQueries({ queryKey: ['materias'] })
    },
  })
}
