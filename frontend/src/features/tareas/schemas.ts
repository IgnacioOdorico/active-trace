import { z } from 'zod'

export const crearTareaSchema = z.object({
  descripcion: z.string().min(1, 'La descripción es requerida'),
  asignado_a: z.string().min(1, 'Seleccione un asignado'),
  materia_id: z
    .string()
    .optional()
    .transform((v) => (v ? v : undefined)),
})

export type CrearTareaFormData = z.infer<typeof crearTareaSchema>

export const comentarioSchema = z.object({
  texto: z.string().min(1, 'El comentario no puede estar vacío'),
})

export type ComentarioFormData = z.infer<typeof comentarioSchema>
