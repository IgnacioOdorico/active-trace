import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { crearTareaSchema, type CrearTareaFormData } from '../schemas'
import { useEditarTarea, useUsuariosAsignables } from '../hooks/useTareasApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { formatNombreUsuario } from '../utils'
import type { Tarea } from '../types'

interface EditarTareaFormProps {
  tarea: Tarea
  onSuccess: () => void
  onCancel: () => void
}

export default function EditarTareaForm({ tarea, onSuccess, onCancel }: EditarTareaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CrearTareaFormData>({
    resolver: zodResolver(crearTareaSchema),
    defaultValues: {
      descripcion: tarea.descripcion,
      asignado_a: tarea.asignado_a,
      materia_id: tarea.materia_id,
    },
  })

  const mutation = useEditarTarea()
  const { data: asignables, isLoading: asignablesLoading } = useUsuariosAsignables()
  const { data: materias, isLoading: materiasLoading } = useMaterias()

  const onSubmit = (values: CrearTareaFormData) => {
    mutation.mutate({ id: tarea.id, payload: values }, { onSuccess })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Descripción</label>
        <textarea
          {...register('descripcion')}
          rows={3}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        {errors.descripcion && (
          <p className="mt-1 text-xs text-red-600">{errors.descripcion.message}</p>
        )}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Asignado a</label>
        <select
          {...register('asignado_a')}
          disabled={asignablesLoading}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="" disabled>
            {asignablesLoading ? 'Cargando docentes...' : 'Seleccione un docente'}
          </option>
          {asignables?.map((u) => (
            <option key={u.id} value={u.id}>
              {formatNombreUsuario(u)} ({u.email})
            </option>
          ))}
        </select>
        {errors.asignado_a && (
          <p className="mt-1 text-xs text-red-600">{errors.asignado_a.message}</p>
        )}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Materia (opcional)
        </label>
        <select
          {...register('materia_id')}
          disabled={materiasLoading}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">
            {materiasLoading ? 'Cargando materias...' : 'Sin materia asociada'}
          </option>
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre}{m.comision ? ` - ${m.comision}` : ''}
            </option>
          ))}
        </select>
      </div>

      {mutation.isError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al editar la tarea.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Guardando...' : 'Guardar cambios'}
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
