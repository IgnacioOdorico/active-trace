import { z } from 'zod'

const baseUsuarioSchema = z.object({
  nombre: z.string().optional().nullable(),
  apellidos: z.string().optional().nullable(),
  email: z.string().email('Email inválido'),
  dni: z.string().optional().nullable(),
  cuil: z.string().optional().nullable(),
  regional: z.string().optional().nullable(),
  legajo: z.string().optional().nullable(),
  legajo_profesional: z.string().optional().nullable(),
  facturador: z.boolean(),
  password: z.string().optional().nullable(),
  // Datos de liquidación/facturación
  banco: z.string().optional().nullable(),
  cbu: z.string().optional().nullable(),
  alias_cbu: z.string().optional().nullable(),
})

// Para modalidad "liquidacion": CBU o alias requeridos
// Para modalidad "factura": facturador=true, datos de facturación opcionales
// Validación condicional según modalidad de cobro (campo UI, no backend)
export const usuarioSchema = baseUsuarioSchema.superRefine((data, ctx) => {
  if (!data.facturador) {
    // Modalidad liquidación: requiere CBU o alias
    if (!data.cbu && !data.alias_cbu) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        message: 'Ingresá CBU o alias CBU para la modalidad de liquidación',
        path: ['cbu'],
      })
    }
  }
})

export type UsuarioFormValues = z.infer<typeof usuarioSchema>
