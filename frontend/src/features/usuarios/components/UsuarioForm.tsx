import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { usuarioSchema, type UsuarioFormValues } from '../schemas'
import { useCrearUsuario, useActualizarUsuario } from '../hooks/useUsuariosApi'
import type { Usuario } from '../types'

interface Props {
  usuario?: Usuario | null
  onSuccess: () => void
}

export default function UsuarioForm({ usuario, onSuccess }: Props) {
  const { mutate: crear, isPending: creando } = useCrearUsuario()
  const { mutate: actualizar, isPending: actualizando } = useActualizarUsuario()
  const isPending = creando || actualizando

  const { register, handleSubmit, watch, setError, formState: { errors } } = useForm<UsuarioFormValues>({
    resolver: zodResolver(usuarioSchema),
    defaultValues: usuario
      ? {
          nombre: usuario.nombre,
          apellidos: usuario.apellidos,
          email: usuario.email,
          dni: usuario.dni,
          cuil: usuario.cuil,
          cbu: usuario.cbu,
          alias_cbu: usuario.alias_cbu,
          banco: usuario.banco,
          regional: usuario.regional,
          legajo: usuario.legajo,
          legajo_profesional: usuario.legajo_profesional,
          facturador: usuario.facturador,
        }
      : { facturador: false },
  })

  const facturador = watch('facturador')

  function onSubmit(values: UsuarioFormValues) {
    const handler = {
      onSuccess,
      onError: (err: unknown) => {
        const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? ''
        setError('root', { message: `Error: ${detail}` })
      },
    }

    if (usuario) {
      const { password: _, ...rest } = values
      actualizar({ id: usuario.id, payload: rest }, handler)
    } else {
      crear({ ...values, facturador: values.facturador ?? false }, handler)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Nombre</label>
          <input {...register('nombre')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Apellidos</label>
          <input {...register('apellidos')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Email *</label>
        <input type="email" {...register('email')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        {errors.email && <p className="text-xs text-red-600">{errors.email.message}</p>}
      </div>

      <div className="grid grid-cols-3 gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">DNI</label>
          <input {...register('dni')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">CUIL</label>
          <input {...register('cuil')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Regional</label>
          <input {...register('regional')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <input type="checkbox" {...register('facturador')} id="facturador" className="rounded" />
        <label htmlFor="facturador" className="text-sm font-medium text-gray-700">
          Modalidad factura (excluido de liquidación general)
        </label>
      </div>

      {!facturador && (
        <div className="grid grid-cols-2 gap-3 rounded-lg bg-blue-50 p-3">
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">CBU</label>
            <input {...register('cbu')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">Alias CBU</label>
            <input {...register('alias_cbu')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-sm font-medium text-gray-700">Banco</label>
            <input {...register('banco')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
          </div>
        </div>
      )}

      {errors.cbu && <p className="text-xs text-red-600">{errors.cbu.message}</p>}

      {!usuario && (
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Contraseña inicial</label>
          <input type="password" {...register('password')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        </div>
      )}

      {errors.root && <p className="rounded bg-red-50 p-2 text-xs text-red-700">{errors.root.message}</p>}

      <div className="flex justify-end">
        <button type="submit" disabled={isPending} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {isPending ? 'Guardando...' : usuario ? 'Actualizar usuario' : 'Crear usuario'}
        </button>
      </div>
    </form>
  )
}
