export interface PreviewRequest {
  materia_id: string
  destinatario_email: string
  asunto_template: string
  cuerpo_template: string
}

export interface PreviewResponse {
  asunto: string
  cuerpo: string
}

export interface EnviarRequest {
  materia_id: string
  destinatarios: string[]
  asunto_template: string
  cuerpo_template: string
}

export interface EnviarResponse {
  lote_id: string
  cantidad: number
  mensaje: string
}

export interface ComunicacionItem {
  id: string
  destinatario: string
  estado: string
  intentos: number
  error_msg: string | null
  enviado_at: string | null
}

export interface TrackingResponse {
  items: ComunicacionItem[]
  total: number
  pagina: number
  por_pagina: number
}
