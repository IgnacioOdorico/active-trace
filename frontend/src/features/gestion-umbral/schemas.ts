import { z } from 'zod'

export const umbralSchema = z.object({
  materia_id: z.string().min(1, 'Seleccione una materia'),
  umbral_pct: z
    .number({ required_error: 'Ingrese un porcentaje' })
    .min(0, 'El porcentaje debe estar entre 0 y 100')
    .max(100, 'El porcentaje debe estar entre 0 y 100'),
  valores_aprobatorios: z.array(z.string()),
})

export type UmbralFormData = z.infer<typeof umbralSchema>
