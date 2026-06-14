// Tipos derivados de los response_model del router /api/encuentros/instancias y /api/guardias

export type EncuentroEstado = 'pendiente' | 'realizado' | 'cancelado'

export interface InstanciaEncuentro {
  id: string
  slot_id: string
  materia_id: string
  materia_nombre: string
  docente_id: string
  docente_nombre: string
  fecha: string
  hora_inicio: string
  hora_fin: string
  estado: EncuentroEstado
  meet_url?: string
  html_url?: string
}

export interface EncuentrosInstanciasResponse {
  data: InstanciaEncuentro[]
  total: number
}

export interface EncuentrosFilters {
  materia_id?: string
  estado?: EncuentroEstado
}

export type GuardiaEstado = 'pendiente' | 'cubierta' | 'sin_cubrir'

export interface Guardia {
  id: string
  materia_id: string
  materia_nombre: string
  docente_ausente_id: string
  docente_ausente_nombre: string
  docente_guardia_id?: string
  docente_guardia_nombre?: string
  fecha: string
  hora_inicio: string
  hora_fin: string
  estado: GuardiaEstado
  comentarios?: string
}

export interface GuardiasResponse {
  data: Guardia[]
  total: number
}

export interface RegistrarGuardiaRequest {
  materia_id: string
  docente_ausente_id: string
  docente_guardia_id?: string
  fecha: string
  hora_inicio: string
  hora_fin: string
  comentarios?: string
}

export interface EditarGuardiaRequest extends Partial<RegistrarGuardiaRequest> {
  estado?: GuardiaEstado
}

export interface GuardiasFilters {
  materia_id?: string
  estado?: GuardiaEstado
  fecha_desde?: string
  fecha_hasta?: string
}
