// Tipos derivados de los response_model del router /api/avisos/*

export type AvisoAlcance = 'Global' | 'PorMateria' | 'PorCohorte' | 'PorRol'
export type AvisoSeveridad = 'Info' | 'Advertencia' | 'Crítico'

export interface Aviso {
  id: string
  tenant_id: string
  alcance: AvisoAlcance
  materia_id?: string
  cohorte_id?: string
  rol_destino?: string
  severidad: AvisoSeveridad
  titulo: string
  cuerpo: string
  inicio_en: string
  fin_en: string
  orden: number
  activo: boolean
  requiere_ack: boolean
  created_at?: string
  updated_at?: string
}

export interface AvisoGestion extends Aviso {
  total_acks: number
}

export interface AvisosGestionResponse {
  items: AvisoGestion[]
  total: number
  pagina: number
  page_size: number
}

export interface AvisosUsuarioResponse {
  items: Aviso[]
  total: number
  pagina: number
  page_size: number
}

export interface CrearAvisoRequest {
  alcance: AvisoAlcance
  materia_id?: string
  cohorte_id?: string
  rol_destino?: string
  severidad: AvisoSeveridad
  titulo: string
  cuerpo: string
  inicio_en: string
  fin_en: string
  orden: number
  activo: boolean
  requiere_ack: boolean
}

export interface EditarAvisoRequest extends Partial<CrearAvisoRequest> {}
