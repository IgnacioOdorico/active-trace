export interface Carrera {
  id: string
  codigo: string
  nombre: string
  descripcion: string | null
  activa: boolean
  created_at: string
  updated_at: string
}

export interface CarreraCreate {
  codigo: string
  nombre: string
  descripcion?: string | null
}

export interface CarreraUpdate {
  nombre?: string
  descripcion?: string | null
  activa?: boolean
}

export interface Cohorte {
  id: string
  nombre: string
  carrera_id: string
  fecha_inicio: string | null
  fecha_fin: string | null
  activa: boolean
  created_at: string
  updated_at: string
}

export interface CohorteCreate {
  nombre: string
  carrera_id: string
  fecha_inicio?: string | null
  fecha_fin?: string | null
}

export interface CohorteUpdate {
  nombre?: string
  fecha_inicio?: string | null
  fecha_fin?: string | null
  activa?: boolean
}

export interface Materia {
  id: string
  codigo: string
  nombre: string
  descripcion: string | null
  carrera_id: string | null
  created_at: string
  updated_at: string
}

export interface MateriaCreate {
  codigo: string
  nombre: string
  descripcion?: string | null
  carrera_id?: string | null
}

export interface MateriaUpdate {
  nombre?: string
  descripcion?: string | null
}
