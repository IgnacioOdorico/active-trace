export interface UmbralConfig {
  umbral_pct: number
  valores_aprobatorios: string[]
  es_default: boolean
  materia_id: string
  materia_nombre: string
}

export interface UmbralUpdateRequest {
  materia_id: string
  umbral_pct?: number
  valores_aprobatorios?: string[]
}

export interface UmbralUpdateResponse {
  umbral_pct: number
  valores_aprobatorios: string[]
  recalculo_count?: number
  mensaje: string
}
