export type EstadoLiquidacion = 'Abierta' | 'Cerrada'

export interface Liquidacion {
  id: string
  usuario_id: string
  docente_nombre: string
  rol: string
  comisiones: string[]
  monto_base: number
  monto_plus: number
  total: number
  es_nexo: boolean
  excluido_por_factura: boolean
  estado: EstadoLiquidacion
  periodo: string
  cohorte_id: string
}

export interface LiquidacionesResponse {
  items: Liquidacion[]
  total: number
}

export interface KpisPeriodo {
  total_general: number
  total_nexo: number
  total_facturas_pendientes: number
  total_facturas_abonadas: number
  cantidad_docentes_general: number
  cantidad_docentes_nexo: number
  cantidad_docentes_facturantes: number
}

export interface HistorialItem {
  id: string
  periodo: string
  cohorte_id: string
  estado: EstadoLiquidacion
  total_docentes: number
  monto_total: number
}

export interface HistorialResponse {
  items: HistorialItem[]
  total: number
}

export interface LiquidacionesFilters {
  cohorte_id?: string
  periodo?: string
}

export interface HistorialFilters {
  desde?: string
  hasta?: string
  estado?: EstadoLiquidacion
}
