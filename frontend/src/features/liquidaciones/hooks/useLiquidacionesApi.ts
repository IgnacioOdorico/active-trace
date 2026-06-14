import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type {
  LiquidacionesResponse,
  KpisPeriodo,
  HistorialResponse,
  LiquidacionesFilters,
  HistorialFilters,
} from '../types'

function buildParams(filters: Record<string, string | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, value)
    }
  }
  return params.toString()
}

export function useLiquidaciones(filters: LiquidacionesFilters) {
  return useQuery({
    queryKey: ['liquidaciones', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<LiquidacionesResponse>(
        `/api/liquidaciones${qs ? `?${qs}` : ''}`,
      )
      return data
    },
    enabled: Boolean(filters.periodo),
  })
}

export function useKpisPeriodo(periodo: string | undefined) {
  return useQuery({
    queryKey: ['liquidaciones-kpis', periodo],
    queryFn: async () => {
      const { data } = await apiClient.get<KpisPeriodo>(
        `/api/liquidaciones/kpis?periodo=${periodo}`,
      )
      return data
    },
    enabled: Boolean(periodo),
  })
}

export function useHistorialLiquidaciones(filters: HistorialFilters) {
  return useQuery({
    queryKey: ['liquidaciones-historial', filters],
    queryFn: async () => {
      const qs = buildParams(filters as Record<string, string | undefined>)
      const { data } = await apiClient.get<HistorialResponse>(
        `/api/liquidaciones/historial${qs ? `?${qs}` : ''}`,
      )
      return data
    },
  })
}

export function useCerrarLiquidacion() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: string) => {
      const { data } = await apiClient.post(`/api/liquidaciones/${id}/cerrar`)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['liquidaciones'] })
      queryClient.invalidateQueries({ queryKey: ['liquidaciones-kpis'] })
    },
  })
}
