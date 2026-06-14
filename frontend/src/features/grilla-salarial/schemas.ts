import { z } from 'zod'

export const salarioBaseSchema = z
  .object({
    rol: z.string().min(1, 'El rol es requerido'),
    monto: z.coerce.number().positive('El monto debe ser positivo'),
    desde: z.string().min(1, 'La fecha desde es requerida'),
    hasta: z.string().optional().nullable(),
  })
  .refine(
    (data) => {
      if (!data.hasta || data.hasta === '') return true
      return data.desde < data.hasta
    },
    {
      message: 'La fecha "desde" debe ser anterior a "hasta"',
      path: ['hasta'],
    },
  )

export type SalarioBaseFormValues = z.infer<typeof salarioBaseSchema>

export const salarioPlusSchema = z
  .object({
    grupo: z.string().min(1, 'El grupo es requerido'),
    rol: z.string().min(1, 'El rol es requerido'),
    monto: z.coerce.number().positive('El monto debe ser positivo'),
    descripcion: z.string().min(1, 'La descripción es requerida'),
    desde: z.string().min(1, 'La fecha desde es requerida'),
    hasta: z.string().optional().nullable(),
  })
  .refine(
    (data) => {
      if (!data.hasta || data.hasta === '') return true
      return data.desde < data.hasta
    },
    {
      message: 'La fecha "desde" debe ser anterior a "hasta"',
      path: ['hasta'],
    },
  )

export type SalarioPlusFormValues = z.infer<typeof salarioPlusSchema>
