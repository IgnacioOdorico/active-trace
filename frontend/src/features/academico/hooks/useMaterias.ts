import { useQuery } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { Materia } from '../types'

export function useMaterias() {
  return useQuery({
    queryKey: ['materias'],
    queryFn: async () => {
      const { data } = await apiClient.get<Materia[]>('/api/v1/estructura/materias')
      return data
    },
  })
}
