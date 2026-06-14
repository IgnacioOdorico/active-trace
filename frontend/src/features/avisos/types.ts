// Tipos derivados de los response_model del router /api/avisos/*

export type AvisoAlcance = 'global' | 'materia' | 'cohorte' | 'rol'
export type AvisoSeveridad = 'info' | 'warning' | 'error'

export interface Aviso {
  id: string
  alcance: AvisoAlcance
  materia_id?: string
  cohorte?: string
  roles: string[]
  severidad: AvisoSeveridad
  titulo: string
  cuerpo: string
  vigencia_inicio: string
  vigencia_fin: string
  orden: number
  activo: boolean
  requiere_ack: boolean
  creado_en: string
}

export interface AvisoGestion extends Aviso {
  total_acks: number
}

export interface AvisosGestionResponse {
  data: AvisoGestion[]
  total: number
}

export interface AvisosUsuarioResponse {
  data: Aviso[]
  total: number
}

export interface CrearAvisoRequest {
  alcance: AvisoAlcance
  materia_id?: string
  cohorte?: string
  roles: string[]
  severidad: AvisoSeveridad
  titulo: string
  cuerpo: string
  vigencia_inicio: string
  vigencia_fin: string
  orden: number
  activo: boolean
  requiere_ack: boolean
}

export interface EditarAvisoRequest extends Partial<CrearAvisoRequest> {}
