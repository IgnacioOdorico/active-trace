// Tipos derivados de los response_model del router /api/tareas/*

export type TareaEstado = 'Pendiente' | 'En progreso' | 'Resuelta' | 'Cancelada'

export interface Tarea {
  id: string
  titulo: string
  descripcion: string
  estado: TareaEstado
  materia_id?: string
  materia_nombre?: string
  asignado_id: string
  asignado_nombre: string
  asignador_id: string
  asignador_nombre: string
  creado_en: string
  actualizado_en: string
}

export interface TareasResponse {
  data: Tarea[]
  total: number
}

export interface ComentarioTarea {
  id: string
  tarea_id: string
  autor_id: string
  autor_nombre: string
  contenido: string
  creado_en: string
}

export interface ComentariosResponse {
  data: ComentarioTarea[]
  total: number
}

export interface CrearTareaRequest {
  titulo: string
  descripcion: string
  asignado_id: string
  materia_id?: string
}

export interface CambiarEstadoRequest {
  estado: TareaEstado
}

export interface AgregarComentarioRequest {
  contenido: string
}

export interface TareasAdminFilters {
  asignado_id?: string
  asignador_id?: string
  materia_id?: string
  estado?: TareaEstado
  q?: string
}
