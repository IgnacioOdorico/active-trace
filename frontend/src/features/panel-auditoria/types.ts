export interface AccionPorDia {
  fecha: string
  total: number
}

export interface ComunicacionPorDocente {
  docente_id: string
  docente_nombre: string
  pendiente: number
  enviando: number
  enviado: number
  fallido: number
  cancelado: number
}

export interface InteraccionDocenteMateria {
  docente_id: string
  docente_nombre: string
  materia_id: string
  materia_nombre: string
  total_acciones: number
  acciones_por_tipo: Record<string, number>
}

export interface AuditLogEntry {
  id: string
  fecha_hora: string
  actor_id: string
  actor_nombre: string
  impersonado_id: string | null
  materia_id: string | null
  materia_nombre: string | null
  accion: string
  detalle: Record<string, unknown> | null
  filas_afectadas: number | null
  ip: string | null
  user_agent: string | null
}

export interface UltimasAccionesResponse {
  items: AuditLogEntry[]
  max_resultados: number
}

export interface PanelFilters {
  desde?: string
  hasta?: string
  materia_id?: string
  actor_id?: string
  accion?: string
}
