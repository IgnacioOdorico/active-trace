import { z } from 'zod'

export const asignacionMasivaSchema = z
  .object({
    usuario_ids: z.array(z.string().min(1)).min(1, 'Seleccione al menos un docente'),
    materia_id: z.string().min(1, 'Seleccione una materia'),
    carrera: z.string().min(1, 'Ingrese la carrera'),
    cohorte: z.string().min(1, 'Ingrese la cohorte'),
    rol: z.string().min(1, 'Seleccione un rol'),
    vigencia_desde: z.string().min(1, 'Ingrese fecha de inicio'),
    vigencia_hasta: z.string().min(1, 'Ingrese fecha de fin'),
  })
  .refine((v) => v.vigencia_desde < v.vigencia_hasta, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['vigencia_hasta'],
  })

export type AsignacionMasivaFormData = z.infer<typeof asignacionMasivaSchema>

export const clonarEquipoSchema = z.object({
  equipo_origen_id: z.string().min(1, 'Seleccione el equipo origen'),
  cohorte_destino: z.string().min(1, 'Ingrese la cohorte destino'),
})

export type ClonarEquipoFormData = z.infer<typeof clonarEquipoSchema>

export const vigenciaSchema = z
  .object({
    vigencia_desde: z.string().min(1, 'Ingrese fecha de inicio'),
    vigencia_hasta: z.string().min(1, 'Ingrese fecha de fin'),
  })
  .refine((v) => v.vigencia_desde < v.vigencia_hasta, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['vigencia_hasta'],
  })

export type VigenciaFormData = z.infer<typeof vigenciaSchema>

export const vigenciaMasivaSchema = vigenciaSchema.and(
  z.object({ equipo_origen_id: z.string().min(1, 'Seleccione el equipo') }),
)

export type VigenciaMasivaFormData = z.infer<typeof vigenciaMasivaSchema>
