import { useQuery } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  AccionPorDia,
  ComunicacionPorDocente,
  InteraccionDocenteMateria,
  UltimasAccionesResponse,
  PanelFilters,
} from '../types'

const BASE = '/api/v1/admin/panel'

function buildParams(filters: Record<string, string | number | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, String(value))
    }
  }
  return params.toString()
}

export function useAccionesPorDia(filters: PanelFilters) {
  return useQuery({
    queryKey: ['panel-acciones-por-dia', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<AccionPorDia[]>(
        `${BASE}/acciones-por-dia${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useComunicacionesPorDocente(filters: PanelFilters) {
  return useQuery({
    queryKey: ['panel-comunicaciones-por-docente', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<ComunicacionPorDocente[]>(
        `${BASE}/comunicaciones-por-docente${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useInteraccionesPorDocenteMateria(filters: PanelFilters) {
  return useQuery({
    queryKey: ['panel-interacciones-por-docente-materia', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<InteraccionDocenteMateria[]>(
        `${BASE}/interacciones-por-docente-materia${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useUltimasAcciones(filters: PanelFilters, max = 200) {
  return useQuery({
    queryKey: ['panel-ultimas-acciones', filters, max],
    queryFn: async () => {
      const qs = buildParams({ ...filters, max } as Record<string, string | number | undefined>)
      const { data } = await apiClient.get<UltimasAccionesResponse>(
        `${BASE}/ultimas-acciones${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}
