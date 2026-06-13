import { useQuery, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { MonitorGeneralResponse, MonitorGeneralFilters, MonitorSeguimientoResponse, MonitorSeguimientoFilters } from '../types'

function buildParams(filters: Record<string, string | number | undefined>): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(filters)) {
    if (value !== undefined && value !== '') {
      params.set(key, String(value))
    }
  }
  return params.toString()
}

export function useMonitorGeneral(filters: MonitorGeneralFilters) {
  return useQuery({
    queryKey: ['monitor-general', filters],
    queryFn: async () => {
      const qs = buildParams(filters)
      const { data } = await apiClient.get<MonitorGeneralResponse>(
        `/api/analisis/monitor-general?${qs}`,
      )
      return data
    },
  })
}

export function useMonitorSeguimiento(filters: MonitorSeguimientoFilters) {
  return useQuery({
    queryKey: ['monitor-seguimiento', filters],
    queryFn: async () => {
      const qs = buildParams(filters)
      const { data } = await apiClient.get<MonitorSeguimientoResponse>(
        `/api/analisis/monitor-seguimiento?${qs}`,
      )
      return data
    },
  })
}

export function useMonitoresApi() {
  const queryClient = useQueryClient()

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ['monitor-general'] })
    queryClient.invalidateQueries({ queryKey: ['monitor-seguimiento'] })
  }

  return { invalidate }
}
