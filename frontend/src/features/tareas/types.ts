// Tipos alineados a los response_model reales de app/schemas/tarea.py.
// El backend no resuelve nombres (asignado/asignador/materia) ni tiene
// columna "titulo" en Tarea: solo expone IDs y descripcion.

export type TareaEstado = 'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada'

export interface Tarea {
  id: string
  descripcion: string
  estado: TareaEstado
  materia_id?: string
  asignado_a: string
  asignado_por: string
  contexto_id?: string
  created_at: string
  updated_at: string
}

export interface TareasResponse {
  items: Tarea[]
  total: number
  pagina: number
  page_size: number
}

export interface ComentarioTarea {
  id: string
  tarea_id: string
  autor_id: string
  texto: string
  creado_at: string
}

export interface ComentariosResponse {
  items: ComentarioTarea[]
  total: number
  pagina: number
  page_size: number
}

export interface CrearTareaRequest {
  descripcion: string
  asignado_a: string
  materia_id?: string
}

export interface CambiarEstadoRequest {
  estado: TareaEstado
}

export interface EditarTareaRequest {
  descripcion?: string
  asignado_a?: string
  materia_id?: string
}

export interface AgregarComentarioRequest {
  texto: string
}

export interface TareasAdminFilters {
  asignado_a?: string
  asignado_por?: string
  materia_id?: string
  estado?: TareaEstado
  busqueda?: string
}

export interface UsuarioAsignable {
  id: string
  nombre: string | null
  apellidos: string | null
  email: string
}
