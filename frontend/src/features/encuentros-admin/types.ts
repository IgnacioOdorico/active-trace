// Tipos alineados a los response_model reales de app/schemas/encuentro.py
// y app/schemas/guardia.py. El backend no resuelve nombres de materia/docente,
// solo expone IDs crudos, y los endpoints de listado devuelven `items`
// (paginado), no `data`.

export type EncuentroEstado = 'Programado' | 'Realizado' | 'Cancelado'

export interface InstanciaEncuentro {
  id: string
  slot_id: string | null
  materia_id: string
  fecha: string
  hora: string
  titulo: string
  estado: EncuentroEstado
  meet_url: string
  video_url?: string
  comentario?: string
}

export interface EncuentrosInstanciasResponse {
  items: InstanciaEncuentro[]
  total: number
  pagina: number
  page_size: number
}

export interface EncuentrosFilters {
  materia_id?: string
  fecha_desde?: string
  fecha_hasta?: string
  estado?: EncuentroEstado
}

export type GuardiaEstado = 'Pendiente' | 'Realizada' | 'Cancelada'

export interface Guardia {
  id: string
  asignacion_id: string
  materia_id: string
  carrera_id: string
  cohorte_id?: string
  dia: string
  horario: string
  estado: GuardiaEstado
  comentarios?: string
}

export interface GuardiasResponse {
  items: Guardia[]
  total: number
  pagina: number
  page_size: number
}

export interface GuardiasFilters {
  materia_id?: string
  asignacion_id?: string
}

export interface RegistrarGuardiaRequest {
  materia_id: string
  carrera_id: string
  cohorte_id?: string
  dia: string
  horario: string
  comentarios?: string
}

export interface EditarGuardiaRequest {
  estado?: GuardiaEstado
  comentarios?: string
}

export interface ExportGuardiasResponse {
  items: Guardia[]
}
