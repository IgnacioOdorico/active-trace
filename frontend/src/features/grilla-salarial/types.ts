export interface SalarioBase {
  id: string
  rol: string
  monto: number
  desde: string
  hasta: string | null
  activo: boolean
}

export interface SalarioBaseCreate {
  rol: string
  monto: number
  desde: string
  hasta?: string | null
}

export interface SalarioBaseUpdate {
  monto?: number
  hasta?: string | null
}

export interface SalarioPlus {
  id: string
  grupo: string
  rol: string
  monto: number
  descripcion: string
  desde: string
  hasta: string | null
  activo: boolean
}

export interface SalarioPlusCreate {
  grupo: string
  rol: string
  monto: number
  descripcion: string
  desde: string
  hasta?: string | null
}

export interface SalarioPlusUpdate {
  monto?: number
  descripcion?: string
  hasta?: string | null
}
