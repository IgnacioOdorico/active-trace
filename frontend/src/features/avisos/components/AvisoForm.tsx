import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { avisoSchema, type AvisoFormData } from '../schemas'
import { useCrearAviso, useEditarAviso } from '../hooks/useAvisosApi'
import type { Aviso } from '../types'

interface AvisoFormProps {
  aviso?: Aviso
  onSuccess: () => void
  onCancel: () => void
}

export default function AvisoForm({ aviso, onSuccess, onCancel }: AvisoFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AvisoFormData>({
    resolver: zodResolver(avisoSchema),
    defaultValues: aviso
      ? {
          alcance: aviso.alcance,
          materia_id: aviso.materia_id,
          cohorte: aviso.cohorte,
          roles: aviso.roles,
          severidad: aviso.severidad,
          titulo: aviso.titulo,
          cuerpo: aviso.cuerpo,
          vigencia_inicio: aviso.vigencia_inicio,
          vigencia_fin: aviso.vigencia_fin,
          orden: aviso.orden,
          activo: aviso.activo,
          requiere_ack: aviso.requiere_ack,
        }
      : { alcance: 'global', severidad: 'info', roles: [], orden: 0, activo: true, requiere_ack: false },
  })

  const alcance = watch('alcance')
  const crearMutation = useCrearAviso()
  const editarMutation = useEditarAviso()
  const isPending = crearMutation.isPending || editarMutation.isPending

  const onSubmit = (values: AvisoFormData) => {
    if (aviso) {
      editarMutation.mutate({ id: aviso.id, payload: values }, { onSuccess })
    } else {
      crearMutation.mutate(values, { onSuccess })
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Alcance</label>
          <select
            {...register('alcance')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="global">Global</option>
            <option value="materia">Por materia</option>
            <option value="cohorte">Por cohorte</option>
            <option value="rol">Por rol</option>
          </select>
          {errors.alcance && <p className="mt-1 text-xs text-red-600">{errors.alcance.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Severidad</label>
          <select
            {...register('severidad')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="info">Info</option>
            <option value="warning">Warning</option>
            <option value="error">Error</option>
          </select>
        </div>
      </div>

      {alcance === 'materia' && (
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Materia ID</label>
          <input
            {...register('materia_id')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            placeholder="ID de la materia"
          />
          {errors.materia_id && (
            <p className="mt-1 text-xs text-red-600">{errors.materia_id.message}</p>
          )}
        </div>
      )}

      {alcance === 'cohorte' && (
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Cohorte</label>
          <input
            {...register('cohorte')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            placeholder="Ej: 2024-1"
          />
          {errors.cohorte && (
            <p className="mt-1 text-xs text-red-600">{errors.cohorte.message}</p>
          )}
        </div>
      )}

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Título</label>
        <input
          {...register('titulo')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        {errors.titulo && <p className="mt-1 text-xs text-red-600">{errors.titulo.message}</p>}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Cuerpo</label>
        <textarea
          {...register('cuerpo')}
          rows={4}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        {errors.cuerpo && <p className="mt-1 text-xs text-red-600">{errors.cuerpo.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Vigencia inicio</label>
          <input
            type="datetime-local"
            {...register('vigencia_inicio')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.vigencia_inicio && (
            <p className="mt-1 text-xs text-red-600">{errors.vigencia_inicio.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Vigencia fin</label>
          <input
            type="datetime-local"
            {...register('vigencia_fin')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.vigencia_fin && (
            <p className="mt-1 text-xs text-red-600">{errors.vigencia_fin.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Orden</label>
          <input
            type="number"
            {...register('orden', { valueAsNumber: true })}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            min={0}
          />
        </div>
        <div className="flex flex-col gap-2 pt-6">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" {...register('activo')} />
            Activo
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" {...register('requiere_ack')} />
            Requiere confirmación de lectura
          </label>
        </div>
      </div>

      {(crearMutation.isError || editarMutation.isError) && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al guardar el aviso. Intente nuevamente.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isPending ? 'Guardando...' : aviso ? 'Actualizar aviso' : 'Crear aviso'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
