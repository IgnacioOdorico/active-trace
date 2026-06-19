export interface ActividadDetectada {
  nombre: string
  tipo: 'numerica' | 'textual'
}

export interface CalificacionPreviewResponse {
  actividades: ActividadDetectada[]
  preview: Record<string, string>[]
  total_filas: number
}

export interface Advertencia {
  fila: number
  motivo: string
}

export interface ImportarResultado {
  insertadas: number
  actualizadas: number
  filas_afectadas: number
  errores: unknown[]
  advertencias: Advertencia[]
}
