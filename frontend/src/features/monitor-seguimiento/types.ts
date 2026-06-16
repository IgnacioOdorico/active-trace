export interface MonitorItem {
  entrada_padron_id: string
  nombre: string
  apellidos: string
  email: string
  comision: string | null
  regional: string | null
  materia_id: string | null
  total_actividades: number
  aprobadas: number
  estado: 'atrasado' | 'al_dia'
}

export interface MonitorPaginacionResponse {
  items: MonitorItem[]
  total: number
  pagina: number
  por_pagina: number
  total_paginas: number
}

export type MonitorGeneralResponse = MonitorPaginacionResponse
export type MonitorSeguimientoResponse = MonitorPaginacionResponse

export interface MonitorGeneralFilters {
  materia_id?: string
  comision?: string
  regional?: string
  q?: string
  estado?: string
  pagina?: number
  por_pagina?: number
}

export interface MonitorSeguimientoFilters {
  alumno_id?: string
  actividad_minima?: string
  fecha_desde?: string
  fecha_hasta?: string
  materia_id?: string
  pagina?: number
  por_pagina?: number
}
