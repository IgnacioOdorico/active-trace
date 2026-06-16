import { z } from 'zod'

export const avisoSchema = z
  .object({
    alcance: z.enum(['Global', 'PorMateria', 'PorCohorte', 'PorRol']),
    materia_id: z.string().optional(),
    cohorte_id: z.string().optional(),
    rol_destino: z.string().optional(),
    severidad: z.enum(['Info', 'Advertencia', 'Crítico']),
    titulo: z.string().min(1, 'El título es requerido'),
    cuerpo: z.string().min(1, 'El cuerpo es requerido'),
    inicio_en: z.string().min(1, 'Ingrese fecha de inicio'),
    fin_en: z.string().min(1, 'Ingrese fecha de fin'),
    orden: z.number().int().min(0),
    activo: z.boolean(),
    requiere_ack: z.boolean(),
  })
  .refine(
    (v) => {
      if (v.alcance === 'PorMateria') return !!v.materia_id
      return true
    },
    { message: 'Seleccione una materia para el alcance "Por materia"', path: ['materia_id'] },
  )
  .refine(
    (v) => {
      if (v.alcance === 'PorCohorte') return !!v.cohorte_id
      return true
    },
    { message: 'Ingrese la cohorte para el alcance "Por cohorte"', path: ['cohorte_id'] },
  )
  .refine((v) => v.inicio_en < v.fin_en, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['fin_en'],
  })

export type AvisoFormData = z.infer<typeof avisoSchema>
