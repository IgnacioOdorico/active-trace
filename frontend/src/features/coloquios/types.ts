// Tipos alineados a los response_model reales de app/schemas/coloquio.py.
// El backend NO resuelve nombres de materia/cohorte ni expone "estado" en el
// listado. "dias_disponibles" es la CANTIDAD de días corridos a generar a
// partir de hoy (entero), no una lista de nombres de día de la semana.

export type TipoEvaluacion = 'Parcial' | 'TP' | 'Coloquio' | 'Recuperatorio'

export interface ColoquioMetricas {
  total_alumnos_convocados: number
  total_instancias_activas: number
  total_reservas_activas: number
  total_notas_registradas: number
}

export interface Convocatoria {
  id: string
  materia_id: string
  cohorte_id: string
  tipo: TipoEvaluacion
  instancia: string
  dias_disponibles: number
  total_convocados: number
  total_reservas_activas: number
  total_cupos_libres: number
}

export interface ConvocatoriasResponse {
  items: Convocatoria[]
  total: number
  pagina: number
  page_size: number
}

export interface CrearConvocatoriaRequest {
  materia_id: string
  cohorte_id: string
  tipo: TipoEvaluacion
  instancia: string
  dias_disponibles: number
  cupo_por_dia: number
}

// El service solo persiste instancia, tipo y dias_disponibles en la edición
// (materia_id, cohorte_id y cupo_por_dia se ignoran si se envían).
export interface EditarConvocatoriaRequest {
  instancia?: string
  tipo?: TipoEvaluacion
  dias_disponibles?: number
}

export interface CerrarConvocatoriaResponse {
  id: string
  estado: string
}

export interface AlumnoConvocatoria {
  alumno_id: string
  nombre: string
  apellidos: string
  email: string
}

export interface ImportarAlumnosRequest {
  alumno_ids: string[]
}

export interface ImportarAlumnosResponse {
  cantidad_importados: number
}
