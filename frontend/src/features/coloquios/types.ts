// Tipos derivados de los response_model del router /api/coloquios/*
// Nota: varios endpoints devuelven response_model=dict — se tipan según los schemas Pydantic del service

export type ColoquioEstado = 'activa' | 'cerrada'

export interface ColoquioMetricas {
  total_alumnos: number
  instancias_activas: number
  reservas_activas: number
  notas_registradas: number
}

export interface Convocatoria {
  id: string
  materia_id: string
  materia_nombre: string
  instancia: string
  dias_disponibles: string[]
  cupo_por_dia: number
  estado: ColoquioEstado
  convocados: number
  reservas_activas: number
  cupos_libres: number
  creado_en: string
}

export interface ConvocatoriasResponse {
  data: Convocatoria[]
  total: number
}

export interface CrearConvocatoriaRequest {
  materia_id: string
  instancia: string
  dias_disponibles: string[]
  cupo_por_dia: number
}

export interface EditarConvocatoriaRequest extends Partial<CrearConvocatoriaRequest> {}

// response_model=dict para cierre — se asume { id, estado }
export interface CerrarConvocatoriaResponse {
  id: string
  estado: ColoquioEstado
}

export interface AlumnoConvocatoria {
  alumno_id: string
  nombre: string
  apellidos: string
  email: string
}

// POST /api/coloquios/{id}/alumnos — response_model=dict
export interface ImportarAlumnosRequest {
  alumno_ids: string[]
}

export interface ImportarAlumnosResponse {
  convocados: number
  importados: number
}
