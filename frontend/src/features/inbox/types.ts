export interface HiloResumen {
  id: string
  remitente_id: string
  destinatario_id: string
  asunto: string
  ultimo_mensaje: string
  leido: boolean
  created_at: string | null
}

export interface Mensaje {
  id: string
  thread_id: string | null
  remitente_id: string
  destinatario_id: string
  asunto: string
  cuerpo: string
  leido: boolean
  created_at: string | null
}

export interface HiloDetalle {
  id: string
  thread_id: string | null
  remitente_id: string
  destinatario_id: string
  asunto: string
  cuerpo: string
  leido: boolean
  created_at: string | null
  respuestas: Mensaje[]
}

export interface InboxResponse {
  items: HiloResumen[]
  total: number
  pagina: number
  page_size: number
}
