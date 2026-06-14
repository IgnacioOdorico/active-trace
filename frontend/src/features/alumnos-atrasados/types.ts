export interface Atrasado {
  id: string
  nombre: string
  apellidos: string
  email: string
  comision: string
  actividades_no_aprobadas: number
  total_actividades: number
  progreso: number
  ultima_actividad: string
}

export interface AtrasadosResponse {
  data: Atrasado[]
  total: number
  pagina: number
  por_pagina: number
}

export interface AtrasadosFilters {
  materia_id?: string
  pagina?: number
  por_pagina?: number
}
