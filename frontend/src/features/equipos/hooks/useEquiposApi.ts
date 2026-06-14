import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  MisEquiposResponse,
  EquiposFilters,
  AsignacionMasivaRequest,
  AsignacionMasivaResponse,
  ClonarEquipoRequest,
  ClonarEquipoResponse,
  ModificarVigenciaRequest,
  ModificarVigenciaResponse,
  VigenciaMasivaRequest,
  VigenciaMasivaResponse,
} from '../types'

function buildParams(filters: Record<string, string | boolean | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, String(value))
    }
  }
  return params.toString()
}

export function useMisEquipos(filters: EquiposFilters = {}) {
  return useQuery({
    queryKey: ['equipos-mis-equipos', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | boolean | undefined>)
      const { data } = await apiClient.get<MisEquiposResponse>(
        `/api/equipos/mis-equipos${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useAsignacionMasiva() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: AsignacionMasivaRequest) => {
      const { data } = await apiClient.post<AsignacionMasivaResponse>(
        '/api/equipos/asignacion-masiva',
        payload,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos-mis-equipos'] })
    },
  })
}

export function useClonarEquipo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: ClonarEquipoRequest) => {
      const { data } = await apiClient.post<ClonarEquipoResponse>(
        '/api/equipos/clonar',
        payload,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos-mis-equipos'] })
    },
  })
}

export function useModificarVigencia() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ id, payload }: { id: string; payload: ModificarVigenciaRequest }) => {
      const { data } = await apiClient.patch<ModificarVigenciaResponse>(
        `/api/equipos/${id}/vigencia`,
        payload,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos-mis-equipos'] })
    },
  })
}

export function useModificarVigenciaMasiva() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: VigenciaMasivaRequest) => {
      const { data } = await apiClient.patch<VigenciaMasivaResponse>(
        '/api/equipos/vigencia-masiva',
        payload,
      )
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['equipos-mis-equipos'] })
    },
  })
}

export function useExportarEquipo() {
  return useMutation({
    mutationFn: async (id: string) => {
      const response = await apiClient.get(`/api/equipos/${id}/exportar`, {
        responseType: 'blob',
      })
      const url = window.URL.createObjectURL(new Blob([response.data as BlobPart]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `equipo-${id}.xlsx`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    },
  })
}
