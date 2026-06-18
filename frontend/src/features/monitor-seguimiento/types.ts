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

// Query params alineados a GET /api/analisis/monitor-seguimiento
// (backend/app/routers/analisis.py). No existe búsqueda de alumno por
// nombre en este endpoint — solo "comision" (texto) y "entrada_padron_id"
// (UUID exacto, sin uso en la UI actual).
export interface MonitorSeguimientoFilters {
  materia_id?: string
  comision?: string
  actividad_minima?: string
  desde?: string
  hasta?: string
  pagina?: number
  por_pagina?: number
}
