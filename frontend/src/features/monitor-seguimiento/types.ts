export interface MonitorAlumno {
  id: string
  nombre: string
  apellidos: string
  email: string
  comision: string
  regional: string
  materia: string
  total_actividades: number
  aprobadas: number
  estado: 'atrasado' | 'al_dia'
}

export interface MonitorGeneralResponse {
  data: MonitorAlumno[]
  total: number
  pagina: number
  por_pagina: number
}

export interface MonitorGeneralFilters {
  materia_id?: string
  comision?: string
  regional?: string
  q?: string
  estado?: string
  pagina?: number
  por_pagina?: number
}

export interface ActividadCalificacion {
  actividad: string
  tipo: string
  calificacion: string | number
  aprobada: boolean
}

export interface SeguimientoAlumno {
  id: string
  nombre: string
  apellidos: string
  email: string
  comision: string
  actividades: ActividadCalificacion[]
}

export interface MonitorSeguimientoResponse {
  data: SeguimientoAlumno[]
  total: number
  pagina: number
  por_pagina: number
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
