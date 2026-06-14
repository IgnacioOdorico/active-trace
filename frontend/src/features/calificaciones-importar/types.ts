export interface ActividadDetectada {
  id: string
  nombre: string
  tipo: 'numerica' | 'textual'
  columnas: string[]
  filas_preview: Record<string, string>[]
}

export interface CalificacionPreviewResponse {
  actividades: ActividadDetectada[]
  total_filas: number
  materia_id: string
  materia_nombre: string
}

export interface Advertencia {
  fila: number
  motivo: string
}

export interface ImportarResultado {
  insertadas: number
  actualizadas: number
  advertencias: Advertencia[]
}
