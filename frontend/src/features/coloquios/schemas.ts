import { z } from 'zod'

const TIPOS_EVALUACION = ['Parcial', 'TP', 'Coloquio', 'Recuperatorio'] as const

export const crearConvocatoriaSchema = z.object({
  materia_id: z.string().min(1, 'Seleccione una materia'),
  cohorte_id: z.string().min(1, 'Seleccione una cohorte'),
  tipo: z.enum(TIPOS_EVALUACION, { error: 'Seleccione un tipo' }),
  instancia: z.string().min(1, 'Ingrese la instancia'),
  dias_disponibles: z
    .number({ error: 'Ingrese la cantidad de días' })
    .int()
    .min(1, 'Debe generarse al menos 1 día'),
  cupo_por_dia: z
    .number({ error: 'Ingrese el cupo por día' })
    .int()
    .min(1, 'El cupo debe ser mayor a 0'),
})

export type CrearConvocatoriaFormData = z.infer<typeof crearConvocatoriaSchema>

export const editarConvocatoriaSchema = z.object({
  tipo: z.enum(TIPOS_EVALUACION, { error: 'Seleccione un tipo' }),
  instancia: z.string().min(1, 'Ingrese la instancia'),
  dias_disponibles: z
    .number({ error: 'Ingrese la cantidad de días' })
    .int()
    .min(1, 'Debe generarse al menos 1 día'),
})

export type EditarConvocatoriaFormData = z.infer<typeof editarConvocatoriaSchema>
