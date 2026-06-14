import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { UmbralConfig, UmbralUpdateRequest, UmbralUpdateResponse } from '../types'

export function useUmbralApi(materiaId: string | null) {
  const queryClient = useQueryClient()

  const current = useQuery({
    queryKey: ['umbral', materiaId],
    queryFn: async () => {
      const { data } = await apiClient.get<UmbralConfig>(
        `/api/umbral?materia_id=${materiaId}`,
      )
      return data
    },
    enabled: !!materiaId,
  })

  const update = useMutation({
    mutationFn: async (params: UmbralUpdateRequest) => {
      const { data } = await apiClient.put<UmbralUpdateResponse>(
        '/api/umbral',
        params,
      )
      return data
    },
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: ['umbral', variables.materia_id] })
    },
  })

  return { current, update }
}
