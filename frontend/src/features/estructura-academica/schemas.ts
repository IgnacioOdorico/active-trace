import { z } from 'zod'

export const carreraSchema = z.object({
  codigo: z.string().min(1, 'El código es requerido'),
  nombre: z.string().min(1, 'El nombre es requerido'),
  descripcion: z.string().optional().nullable(),
})

export type CarreraFormValues = z.infer<typeof carreraSchema>

export const cohorteSchema = z
  .object({
    nombre: z.string().min(1, 'El nombre es requerido'),
    carrera_id: z.string().min(1, 'La carrera es requerida'),
    fecha_inicio: z.string().optional().nullable(),
    fecha_fin: z.string().optional().nullable(),
  })
  .refine(
    (data) => {
      if (!data.fecha_inicio || !data.fecha_fin) return true
      return data.fecha_inicio < data.fecha_fin
    },
    {
      message: 'La fecha de inicio debe ser anterior a la fecha de fin',
      path: ['fecha_fin'],
    },
  )

export type CohorteFormValues = z.infer<typeof cohorteSchema>

export const materiaSchema = z.object({
  codigo: z.string().min(1, 'El código es requerido'),
  nombre: z.string().min(1, 'El nombre es requerido'),
  descripcion: z.string().optional().nullable(),
  carrera_id: z.string().optional().nullable(),
})

export type MateriaFormValues = z.infer<typeof materiaSchema>
