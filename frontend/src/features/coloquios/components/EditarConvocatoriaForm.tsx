import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { editarConvocatoriaSchema, type EditarConvocatoriaFormData } from '../schemas'
import { useEditarConvocatoria } from '../hooks/useColoquiosApi'
import type { Convocatoria } from '../types'

const TIPOS_EVALUACION = ['Parcial', 'TP', 'Coloquio', 'Recuperatorio'] as const

interface EditarConvocatoriaFormProps {
  convocatoria: Convocatoria
  onSuccess: () => void
  onCancel: () => void
}

export default function EditarConvocatoriaForm({
  convocatoria,
  onSuccess,
  onCancel,
}: EditarConvocatoriaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<EditarConvocatoriaFormData>({
    resolver: zodResolver(editarConvocatoriaSchema),
    defaultValues: {
      tipo: convocatoria.tipo,
      instancia: convocatoria.instancia,
      dias_disponibles: convocatoria.dias_disponibles,
    },
  })

  const editarMutation = useEditarConvocatoria()

  const onSubmit = (values: EditarConvocatoriaFormData) => {
    editarMutation.mutate({ id: convocatoria.id, payload: values }, { onSuccess })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <p className="text-xs text-gray-500">
        Materia y cohorte no se pueden modificar una vez creada la convocatoria.
      </p>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="editar-tipo" className="mb-1 block text-sm font-medium text-gray-700">
            Tipo
          </label>
          <select
            id="editar-tipo"
            {...register('tipo')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            {TIPOS_EVALUACION.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
          {errors.tipo && <p className="mt-1 text-xs text-red-600">{errors.tipo.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Instancia</label>
          <input
            {...register('instancia')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.instancia && (
            <p className="mt-1 text-xs text-red-600">{errors.instancia.message}</p>
          )}
        </div>
      </div>

      <div>
        <label htmlFor="editar-dias" className="mb-1 block text-sm font-medium text-gray-700">
          Cantidad de días a generar
        </label>
        <input
          id="editar-dias"
          type="number"
          {...register('dias_disponibles', { valueAsNumber: true })}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          min={1}
        />
        {errors.dias_disponibles && (
          <p className="mt-1 text-xs text-red-600">{errors.dias_disponibles.message}</p>
        )}
      </div>

      {editarMutation.isError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al actualizar la convocatoria.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={editarMutation.isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {editarMutation.isPending ? 'Guardando...' : 'Actualizar convocatoria'}
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
