import { z } from 'zod'

export const ROLES_EQUIPO = ['PROFESOR', 'TUTOR', 'NEXO'] as const

export const asignacionMasivaSchema = z
  .object({
    usuario_ids: z.array(z.string().min(1)).min(1, 'Seleccione al menos un docente'),
    materia_id: z.string().min(1, 'Seleccione una materia'),
    carrera_id: z.string().min(1, 'Seleccione una carrera'),
    cohorte_id: z.string().min(1, 'Seleccione una cohorte'),
    rol: z.enum(ROLES_EQUIPO, { error: 'Seleccione un rol' }),
    desde: z.string().min(1, 'Ingrese fecha de inicio'),
    hasta: z.string().optional(),
  })
  .refine((v) => !v.hasta || v.desde < v.hasta, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['hasta'],
  })

export type AsignacionMasivaFormData = z.infer<typeof asignacionMasivaSchema>

export const clonarEquipoSchema = z
  .object({
    materia_id: z.string().min(1, 'Seleccione una materia'),
    cohorte_origen_id: z.string().min(1, 'Seleccione la cohorte origen'),
    cohorte_destino_id: z.string().min(1, 'Seleccione la cohorte destino'),
    desde: z.string().min(1, 'Ingrese fecha de inicio'),
    hasta: z.string().optional(),
  })
  .refine((v) => v.cohorte_origen_id !== v.cohorte_destino_id, {
    message: 'La cohorte destino debe ser distinta de la cohorte origen',
    path: ['cohorte_destino_id'],
  })
  .refine((v) => !v.hasta || v.desde < v.hasta, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['hasta'],
  })

export type ClonarEquipoFormData = z.infer<typeof clonarEquipoSchema>

export const vigenciaSchema = z
  .object({
    desde: z.string().min(1, 'Ingrese fecha de inicio'),
    hasta: z.string().min(1, 'Ingrese fecha de fin'),
  })
  .refine((v) => v.desde < v.hasta, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['hasta'],
  })

export type VigenciaFormData = z.infer<typeof vigenciaSchema>

export const vigenciaMasivaSchema = z
  .object({
    materia_id: z.string().min(1, 'Seleccione una materia'),
    cohorte_id: z.string().min(1, 'Seleccione una cohorte'),
    desde: z.string().min(1, 'Ingrese fecha de inicio'),
    hasta: z.string().optional(),
  })
  .refine((v) => !v.hasta || v.desde < v.hasta, {
    message: 'La fecha de inicio debe ser anterior a la de fin',
    path: ['hasta'],
  })

export type VigenciaMasivaFormData = z.infer<typeof vigenciaMasivaSchema>
