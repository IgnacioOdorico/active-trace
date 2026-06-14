import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { convocatoriaSchema, type ConvocatoriaFormData } from '../schemas'
import { useCrearConvocatoria, useEditarConvocatoria } from '../hooks/useColoquiosApi'
import type { Convocatoria } from '../types'

const DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

interface ConvocatoriaFormProps {
  convocatoria?: Convocatoria
  onSuccess: () => void
  onCancel: () => void
}

export default function ConvocatoriaForm({
  convocatoria,
  onSuccess,
  onCancel,
}: ConvocatoriaFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<ConvocatoriaFormData>({
    resolver: zodResolver(convocatoriaSchema),
    defaultValues: convocatoria
      ? {
          materia_id: convocatoria.materia_id,
          instancia: convocatoria.instancia,
          dias_disponibles: convocatoria.dias_disponibles,
          cupo_por_dia: convocatoria.cupo_por_dia,
        }
      : { dias_disponibles: [] },
  })

  const diasSeleccionados = watch('dias_disponibles') ?? []
  const crearMutation = useCrearConvocatoria()
  const editarMutation = useEditarConvocatoria()
  const isPending = crearMutation.isPending || editarMutation.isPending

  const toggleDia = (dia: string) => {
    const actual = diasSeleccionados
    if (actual.includes(dia)) {
      setValue('dias_disponibles', actual.filter((d) => d !== dia))
    } else {
      setValue('dias_disponibles', [...actual, dia])
    }
  }

  const onSubmit = (values: ConvocatoriaFormData) => {
    if (convocatoria) {
      editarMutation.mutate({ id: convocatoria.id, payload: values }, { onSuccess })
    } else {
      crearMutation.mutate(values, { onSuccess })
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
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
          <label className="mb-1 block text-sm font-medium text-gray-700">Instancia</label>
          <input
            {...register('instancia')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            placeholder="Ej: Primer llamado"
          />
          {errors.instancia && (
            <p className="mt-1 text-xs text-red-600">{errors.instancia.message}</p>
          )}
        </div>
      </div>

      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">Días disponibles</label>
        <div className="flex flex-wrap gap-2">
          {DIAS_SEMANA.map((dia) => (
            <button
              key={dia}
              type="button"
              onClick={() => toggleDia(dia)}
              className={`rounded-full px-3 py-1 text-sm font-medium transition-colors ${
                diasSeleccionados.includes(dia)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {dia}
            </button>
          ))}
        </div>
        {errors.dias_disponibles && (
          <p className="mt-1 text-xs text-red-600">{errors.dias_disponibles.message}</p>
        )}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Cupo por día</label>
        <input
          type="number"
          {...register('cupo_por_dia', { valueAsNumber: true })}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          min={1}
        />
        {errors.cupo_por_dia && (
          <p className="mt-1 text-xs text-red-600">{errors.cupo_por_dia.message}</p>
        )}
      </div>

      {(crearMutation.isError || editarMutation.isError) && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al guardar la convocatoria.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isPending
            ? 'Guardando...'
            : convocatoria
            ? 'Actualizar convocatoria'
            : 'Crear convocatoria'}
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
