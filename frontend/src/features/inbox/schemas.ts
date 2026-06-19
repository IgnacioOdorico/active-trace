import { z } from 'zod'

export const responderSchema = z.object({
  cuerpo: z.string().min(1, 'El mensaje no puede estar vacío'),
})

export type ResponderFormData = z.infer<typeof responderSchema>
