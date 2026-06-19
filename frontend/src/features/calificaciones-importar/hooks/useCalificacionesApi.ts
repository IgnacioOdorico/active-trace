import { useMutation } from '@tanstack/react-query'
import apiClient from '../../../shared/services/httpClient'
import type { CalificacionPreviewResponse, ImportarResultado } from '../types'

interface PreviewParams {
  materia_id: string
  file: File
}

interface ImportarParams {
  materia_id: string
  actividades: string[]
  file: File
}

export function useCalificacionesApi() {
  const preview = useMutation({
    mutationFn: async ({ materia_id, file }: PreviewParams) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('materia_id', materia_id)
      const { data } = await apiClient.post<CalificacionPreviewResponse>(
        '/api/calificaciones/preview',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      )
      return data
    },
  })

  const importar = useMutation({
    mutationFn: async ({ materia_id, actividades, file }: ImportarParams) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('materia_id', materia_id)
      formData.append('actividades', JSON.stringify(actividades))
      const { data } = await apiClient.post<ImportarResultado>(
        '/api/calificaciones/importar',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } },
      )
      return data
    },
  })

  return { preview, importar }
}
