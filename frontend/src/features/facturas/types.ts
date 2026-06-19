export type EstadoFactura = 'Pendiente' | 'Abonada'

export interface Factura {
  id: string
  usuario_id: string
  periodo: string
  detalle: string
  referencia_archivo: string
  tamano_kb: number
  estado: EstadoFactura
  cargada_at: string
  abonada_at: string | null
}

export interface FacturasFilters {
  periodo?: string
  estado?: EstadoFactura
}
