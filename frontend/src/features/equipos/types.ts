// Tipos derivados de los response_model del router /api/equipos/*

export interface MiEquipo {
  id: string
  materia_id: string
  materia_nombre: string
  carrera: string
  cohorte: string
  comisiones: string[]
  rol: string
  vigencia_desde: string
  vigencia_hasta: string
  activo: boolean
}

export interface MisEquiposResponse {
  data: MiEquipo[]
  total: number
}

export interface AsignacionMasivaRequest {
  usuario_ids: string[]
  materia_id: string
  carrera_id: string
  cohorte_id: string
  rol: string
  desde: string
  hasta?: string
}

export interface AsignacionMasivaResponse {
  ids_creados: string[]
}

export interface DocenteDisponible {
  id: string
  nombre_completo: string
  email: string
  roles: string[]
}

export interface ClonarEquipoRequest {
  materia_id: string
  cohorte_origen_id: string
  cohorte_destino_id: string
  desde: string
  hasta?: string
}

export interface ClonarEquipoResponse {
  ids_creados: string[]
}

export interface ModificarVigenciaRequest {
  desde: string
  hasta: string
}

export interface ModificarVigenciaResponse {
  id: string
  vigencia_desde: string
  vigencia_hasta: string
}

export interface VigenciaMasivaRequest {
  materia_id: string
  cohorte_id: string
  desde: string
  hasta?: string
}

export interface VigenciaMasivaResponse {
  filas_afectadas: number
}

export interface EquiposFilters {
  materia_id?: string
  rol?: string
  activo?: boolean
}
