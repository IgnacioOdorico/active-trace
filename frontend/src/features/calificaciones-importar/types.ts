export interface ActividadDetectada {
  nombre: string
  tipo: 'numerica' | 'textual'
}

export interface CalificacionPreviewResponse {
  actividades: ActividadDetectada[]
  preview: Record<string, string>[]
  total_filas: number
  materia_id: string
  materia_nombre: string
}

export interface Advertencia {
  fila: number
  tipo: string
  detalle: string
  actividad?: string
  valor?: string
}

export interface ImportarResultado {
  insertadas: number
  actualizadas: number
  filas_afectadas: number
  errores: unknown[]
  advertencias: Advertencia[]
}
