export interface PerfilResponse {
  id: string
  tenant_id: string
  email: string
  nombre: string | null
  apellidos: string | null
  dni: string | null
  cuil: string | null
  cbu: string | null
  alias_cbu: string | null
  banco: string | null
  regional: string | null
  legajo: string | null
  legajo_profesional: string | null
  facturador: boolean
  estado: string
  is_active: boolean
  created_at: string | null
  updated_at: string | null
}

export interface PerfilUpdate {
  nombre?: string | null
  apellidos?: string | null
  dni?: string | null
  cbu?: string | null
  alias_cbu?: string | null
  banco?: string | null
  regional?: string | null
  email?: string | null
  legajo_profesional?: string | null
  facturador?: boolean | null
}
