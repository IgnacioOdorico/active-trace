// Tipos derivados de los response_model de /api/programas y /api/fechas-academicas
// Nota: endpoints devuelven response_model=dict — tipados según los schemas Pydantic del service

export interface Programa {
  id: string
  materia_id: string
  materia_nombre: string
  carrera: string
  cohorte: string
  url?: string
  nombre_archivo?: string
  creado_en: string
}

export interface ProgramasResponse {
  data: Programa[]
  total: number
}

export interface SubirProgramaRequest {
  materia_id: string
  carrera: string
  cohorte: string
  // El archivo se sube como multipart/form-data en el componente
}

export type TipoEvaluacion = 'parcial' | 'tp' | 'coloquio'

export interface FechaAcademica {
  id: string
  materia_id: string
  materia_nombre: string
  cohorte: string
  tipo: TipoEvaluacion
  numero: number
  fecha: string
  descripcion?: string
  creado_en: string
}

export interface FechasAcademicasResponse {
  data: FechaAcademica[]
  total: number
}

export interface CrearFechaAcademicaRequest {
  materia_id: string
  cohorte: string
  tipo: TipoEvaluacion
  numero: number
  fecha: string
  descripcion?: string
}

export interface EditarFechaAcademicaRequest extends Partial<CrearFechaAcademicaRequest> {}

export interface FechasFilters {
  materia_id?: string
  cohorte?: string
  tipo?: TipoEvaluacion
}
