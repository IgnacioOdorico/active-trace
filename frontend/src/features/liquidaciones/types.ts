export type EstadoLiquidacion = 'Abierta' | 'Cerrada'

export interface PlusDetalle {
  grupo: string
  monto: number
}

export interface Liquidacion {
  id: string
  usuario_id: string
  docente_nombre: string
  rol: string
  comisiones: number
  monto_base: number
  plus_detalle: PlusDetalle[]
  monto_total: number
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
  cantidad_general: number
  cantidad_nexo: number
  cantidad_facturantes: number
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
  docente_id?: string
}

export interface HistorialFilters {
  desde?: string
  hasta?: string
  estado?: EstadoLiquidacion
}
