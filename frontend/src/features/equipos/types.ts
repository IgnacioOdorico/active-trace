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
  carrera: string
  cohorte: string
  rol: string
  vigencia_desde: string
  vigencia_hasta: string
}

export interface AsignacionMasivaResponse {
  ids_creados: string[]
  total: number
}

export interface ClonarEquipoRequest {
  equipo_origen_id: string
  cohorte_destino: string
}

export interface ClonarEquipoResponse {
  ids_creados: string[]
  total: number
}

export interface ModificarVigenciaRequest {
  vigencia_desde: string
  vigencia_hasta: string
}

export interface ModificarVigenciaResponse {
  id: string
  vigencia_desde: string
  vigencia_hasta: string
}

export interface VigenciaMasivaRequest {
  equipo_origen_id: string
  vigencia_desde: string
  vigencia_hasta: string
}

export interface VigenciaMasivaResponse {
  filas_afectadas: number
}

export interface EquiposFilters {
  materia_id?: string
  rol?: string
  activo?: boolean
}
