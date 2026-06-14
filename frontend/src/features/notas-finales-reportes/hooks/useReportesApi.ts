import { useQuery, useMutation } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { ReportesMetrics, ActividadInfo, NotasFinalesResponse, NotaFinalRequest } from '../types'

export function useReportesApi(materiaId: string | null) {
  const metrics = useQuery({
    queryKey: ['reportes-metrics', materiaId],
    queryFn: async () => {
      const { data } = await apiClient.get<ReportesMetrics>(
        `/api/analisis/reportes/${materiaId}`,
      )
      return data
    },
    enabled: !!materiaId,
  })

  const actividades = useQuery({
    queryKey: ['reportes-actividades', materiaId],
    queryFn: async () => {
      const { data } = await apiClient.get<ActividadInfo[]>(
        `/api/analisis/reportes/${materiaId}/actividades`,
      )
      return data
    },
    enabled: !!materiaId,
  })

  const calcularNotaFinal = useMutation({
    mutationFn: async (params: NotaFinalRequest) => {
      const { data } = await apiClient.post<NotasFinalesResponse>(
        '/api/analisis/notas-finales',
        params,
      )
      return data
    },
  })

  return { metrics, actividades, calcularNotaFinal }
}
