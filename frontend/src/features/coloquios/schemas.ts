import { z } from 'zod'

export const convocatoriaSchema = z.object({
  materia_id: z.string().min(1, 'Seleccione una materia'),
  instancia: z.string().min(1, 'Ingrese la instancia'),
  dias_disponibles: z
    .array(z.string())
    .min(1, 'Seleccione al menos un día disponible'),
  cupo_por_dia: z
    .number({ required_error: 'Ingrese el cupo por día' })
    .int()
    .min(1, 'El cupo debe ser mayor a 0'),
})

export type ConvocatoriaFormData = z.infer<typeof convocatoriaSchema>
