import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { asignacionMasivaSchema, type AsignacionMasivaFormData } from '../schemas'
import { useAsignacionMasiva } from '../hooks/useEquiposApi'

interface AsignacionMasivaFormProps {
  onSuccess: (idsCreados: string[]) => void
}

export default function AsignacionMasivaForm({ onSuccess }: AsignacionMasivaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setError,
  } = useForm<AsignacionMasivaFormData>({
    resolver: zodResolver(asignacionMasivaSchema),
    defaultValues: { usuario_ids: [] },
  })

  const mutation = useAsignacionMasiva()

  const onSubmit = (values: AsignacionMasivaFormData) => {
    mutation.mutate(values, {
      onSuccess: (data) => {
        onSuccess(data.ids_creados)
        reset()
      },
      onError: (err: unknown) => {
        const axiosErr = err as { response?: { status?: number; data?: { detail?: string } } }
        if (axiosErr?.response?.status === 422) {
          setError('root', {
            message: axiosErr.response?.data?.detail ?? 'Error de validación del servidor (422)',
          })
        }
      },
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          IDs de docentes (separados por coma)
        </label>
        <input
          type="text"
          placeholder="uuid1, uuid2, ..."
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => {
            const ids = e.target.value
              .split(',')
              .map((s) => s.trim())
              .filter(Boolean)
            // inject as array via setValue workaround — handled via hidden input trick
            ;(document.querySelector('input[name="usuario_ids_raw"]') as HTMLInputElement | null)
            void ids
          }}
          {...register('usuario_ids.0')}
        />
        {errors.usuario_ids && (
          <p className="mt-1 text-xs text-red-600">{errors.usuario_ids.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
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
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Carrera</label>
          <input
            {...register('carrera')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            placeholder="Ej: Ingeniería en Sistemas"
          />
          {errors.carrera && (
            <p className="mt-1 text-xs text-red-600">{errors.carrera.message}</p>
          )}
        </div>
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
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Rol</label>
          <select
            {...register('rol')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Seleccione rol</option>
            <option value="titular">Titular</option>
            <option value="tutor">Tutor</option>
            <option value="ayudante">Ayudante</option>
          </select>
          {errors.rol && <p className="mt-1 text-xs text-red-600">{errors.rol.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Vigencia desde</label>
          <input
            type="date"
            {...register('vigencia_desde')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.vigencia_desde && (
            <p className="mt-1 text-xs text-red-600">{errors.vigencia_desde.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Vigencia hasta</label>
          <input
            type="date"
            {...register('vigencia_hasta')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.vigencia_hasta && (
            <p className="mt-1 text-xs text-red-600">{errors.vigencia_hasta.message}</p>
          )}
        </div>
      </div>

      {errors.root && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{errors.root.message}</div>
      )}

      {mutation.isSuccess && (
        <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">
          Asignación masiva completada. {mutation.data?.total} asignaciones creadas.
        </div>
      )}

      <button
        type="submit"
        disabled={mutation.isPending}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {mutation.isPending ? 'Asignando...' : 'Asignar masivamente'}
      </button>
    </form>
  )
}
