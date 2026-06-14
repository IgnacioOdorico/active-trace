import { z } from 'zod'

export const crearTareaSchema = z.object({
  titulo: z.string().min(1, 'El título es requerido'),
  descripcion: z.string().min(1, 'La descripción es requerida'),
  asignado_id: z.string().min(1, 'Seleccione un asignado'),
  materia_id: z.string().optional(),
})

export type CrearTareaFormData = z.infer<typeof crearTareaSchema>

export const comentarioSchema = z.object({
  contenido: z.string().min(1, 'El comentario no puede estar vacío'),
})

export type ComentarioFormData = z.infer<typeof comentarioSchema>
