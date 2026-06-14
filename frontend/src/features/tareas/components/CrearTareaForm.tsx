import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { crearTareaSchema, type CrearTareaFormData } from '../schemas'
import { useCrearTarea } from '../hooks/useTareasApi'

interface CrearTareaFormProps {
  onSuccess: () => void
  onCancel: () => void
}

export default function CrearTareaForm({ onSuccess, onCancel }: CrearTareaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CrearTareaFormData>({
    resolver: zodResolver(crearTareaSchema),
  })

  const mutation = useCrearTarea()

  const onSubmit = (values: CrearTareaFormData) => {
    mutation.mutate(values, {
      onSuccess: () => {
        onSuccess()
        reset()
      },
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Título</label>
        <input
          {...register('titulo')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        {errors.titulo && <p className="mt-1 text-xs text-red-600">{errors.titulo.message}</p>}
      </div>

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
        <label className="mb-1 block text-sm font-medium text-gray-700">ID del asignado</label>
        <input
          {...register('asignado_id')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          placeholder="UUID del docente asignado"
        />
        {errors.asignado_id && (
          <p className="mt-1 text-xs text-red-600">{errors.asignado_id.message}</p>
        )}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          Materia ID (opcional)
        </label>
        <input
          {...register('materia_id')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          placeholder="ID de la materia (opcional)"
        />
      </div>

      {mutation.isError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al crear la tarea.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={mutation.isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Creando...' : 'Crear tarea'}
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
