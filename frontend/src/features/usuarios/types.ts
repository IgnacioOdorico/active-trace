export type ModalidadCobro = 'liquidacion' | 'factura'

export interface Usuario {
  id: string
  tenant_id: string
  nombre: string | null
  apellidos: string | null
  email: string
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
  created_at: string
  updated_at: string
}

export interface UsuarioListResponse {
  data: Usuario[]
  total: number
  page: number
  page_size: number
}

export interface UsuarioCreate {
  nombre?: string | null
  apellidos?: string | null
  email: string
  dni?: string | null
  cuil?: string | null
  cbu?: string | null
  alias_cbu?: string | null
  banco?: string | null
  regional?: string | null
  legajo?: string | null
  legajo_profesional?: string | null
  facturador: boolean
  estado?: string
  password?: string | null
}

export interface UsuarioUpdate {
  nombre?: string | null
  apellidos?: string | null
  email?: string | null
  dni?: string | null
  cuil?: string | null
  cbu?: string | null
  alias_cbu?: string | null
  banco?: string | null
  regional?: string | null
  legajo?: string | null
  legajo_profesional?: string | null
  facturador?: boolean | null
  estado?: string | null
}

export interface UsuariosFilters {
  estado?: string
  page?: number
  page_size?: number
}
