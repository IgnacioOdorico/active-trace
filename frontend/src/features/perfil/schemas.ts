import { z } from 'zod'

export const perfilSchema = z.object({
  nombre: z.string().min(1, 'El nombre es requerido').nullable().optional(),
  apellidos: z.string().min(1, 'Los apellidos son requeridos').nullable().optional(),
  dni: z.string().nullable().optional(),
  cbu: z.string().nullable().optional(),
  alias_cbu: z.string().nullable().optional(),
  banco: z.string().nullable().optional(),
  regional: z.string().nullable().optional(),
  email: z.string().email('Email inválido').nullable().optional(),
  legajo_profesional: z.string().nullable().optional(),
  facturador: z.boolean().nullable().optional(),
})

export type PerfilFormData = z.infer<typeof perfilSchema>
