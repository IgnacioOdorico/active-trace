import { z } from 'zod'

export const avisoSchema = z
  .object({
    alcance: z.enum(['global', 'materia', 'cohorte', 'rol']),
    materia_id: z.string().optional(),
    cohorte: z.string().optional(),
    roles: z.array(z.string()),
    severidad: z.enum(['info', 'warning', 'error']),
    titulo: z.string().min(1, 'El título es requerido'),
    cuerpo: z.string().min(1, 'El cuerpo es requerido'),
    vigencia_inicio: z.string().min(1, 'Ingrese fecha de inicio'),
    vigencia_fin: z.string().min(1, 'Ingrese fecha de fin'),
    orden: z.number().int().min(0),
    activo: z.boolean(),
    requiere_ack: z.boolean(),
  })
  .refine(
    (v) => {
      if (v.alcance === 'materia') return !!v.materia_id
      return true
    },
    { message: 'Seleccione una materia para el alcance "materia"', path: ['materia_id'] },
  )
  .refine(
    (v) => {
      if (v.alcance === 'cohorte') return !!v.cohorte
      return true
    },
    { message: 'Ingrese la cohorte para el alcance "cohorte"', path: ['cohorte'] },
  )
  .refine((v) => v.vigencia_inicio < v.vigencia_fin, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['vigencia_fin'],
  })

export type AvisoFormData = z.infer<typeof avisoSchema>
