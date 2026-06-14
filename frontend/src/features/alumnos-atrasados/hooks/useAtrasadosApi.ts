import { useQuery } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { AtrasadosResponse, AtrasadosFilters } from '../types'

export function useAtrasadosApi(filters: AtrasadosFilters) {
  return useQuery({
    queryKey: ['atrasados', filters],
    queryFn: async () => {
      const params = new URLSearchParams()
      if (filters.materia_id) params.set('materia_id', filters.materia_id)
      if (filters.pagina) params.set('pagina', String(filters.pagina))
      if (filters.por_pagina) params.set('por_pagina', String(filters.por_pagina))
      const { data } = await apiClient.get<AtrasadosResponse>(
        `/api/analisis/atrasados?${params}`,
      )
      return data
    },
    enabled: !!filters.materia_id,
  })
}
