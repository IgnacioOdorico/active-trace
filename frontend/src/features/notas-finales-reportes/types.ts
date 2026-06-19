export interface ReportesMetrics {
  total_alumnos: number
  total_actividades: number
  total_calificaciones: number
  promedio_aprobacion_general: number
  alumnos_atrasados_count: number
  alumnos_aprobados_count: number
  sin_datos: boolean
}

export interface ActividadInfo {
  id: string
  nombre: string
  tipo: 'numerica' | 'textual'
}

export interface NotaFinalRequest {
  materia_id: string
  actividades: string[]
}

export interface NotaFinalAlumno {
  nombre: string
  apellidos: string
  comision: string
  nota_final: number | null
  actividades_textuales: string[]
  estado: 'aprobado' | 'no_aprobado'
}

export interface NotasFinalesResponse {
  alumnos: NotaFinalAlumno[]
}
