import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { crearConvocatoriaSchema, type CrearConvocatoriaFormData } from '../schemas'
import { useCrearConvocatoria } from '../hooks/useColoquiosApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'

const TIPOS_EVALUACION = ['Parcial', 'TP', 'Coloquio', 'Recuperatorio'] as const

interface ConvocatoriaFormProps {
  onSuccess: () => void
  onCancel: () => void
}

export default function ConvocatoriaForm({ onSuccess, onCancel }: ConvocatoriaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CrearConvocatoriaFormData>({
    resolver: zodResolver(crearConvocatoriaSchema),
  })

  const crearMutation = useCrearConvocatoria()
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const { data: cohortes, isLoading: cohortesLoading } = useCohortes()

  const onSubmit = (values: CrearConvocatoriaFormData) => {
    crearMutation.mutate(values, { onSuccess })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="convocatoria-materia" className="mb-1 block text-sm font-medium text-gray-700">
            Materia
          </label>
          <select
            id="convocatoria-materia"
            {...register('materia_id')}
            disabled={materiasLoading}
            defaultValue=""
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="" disabled>
              {materiasLoading ? 'Cargando materias...' : 'Seleccione una materia'}
            </option>
            {materias?.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nombre}
                {m.comision ? ` - ${m.comision}` : ''}
              </option>
            ))}
          </select>
          {errors.materia_id && (
            <p className="mt-1 text-xs text-red-600">{errors.materia_id.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="convocatoria-cohorte" className="mb-1 block text-sm font-medium text-gray-700">
            Cohorte
          </label>
          <select
            id="convocatoria-cohorte"
            {...register('cohorte_id')}
            disabled={cohortesLoading}
            defaultValue=""
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="" disabled>
              {cohortesLoading ? 'Cargando cohortes...' : 'Seleccione una cohorte'}
            </option>
            {cohortes?.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
          {errors.cohorte_id && (
            <p className="mt-1 text-xs text-red-600">{errors.cohorte_id.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="convocatoria-tipo" className="mb-1 block text-sm font-medium text-gray-700">
            Tipo
          </label>
          <select
            id="convocatoria-tipo"
            {...register('tipo')}
            defaultValue=""
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="" disabled>
              Seleccione un tipo
            </option>
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
            placeholder="Ej: Primer llamado"
          />
          {errors.instancia && (
            <p className="mt-1 text-xs text-red-600">{errors.instancia.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="convocatoria-dias" className="mb-1 block text-sm font-medium text-gray-700">
            Cantidad de días a generar
          </label>
          <input
            id="convocatoria-dias"
            type="number"
            {...register('dias_disponibles', { valueAsNumber: true })}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            min={1}
          />
          <p className="mt-1 text-xs text-gray-500">
            Se generan turnos a partir de mañana, uno por cada día corrido.
          </p>
          {errors.dias_disponibles && (
            <p className="mt-1 text-xs text-red-600">{errors.dias_disponibles.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="convocatoria-cupo" className="mb-1 block text-sm font-medium text-gray-700">
            Cupo por día
          </label>
          <input
            id="convocatoria-cupo"
            type="number"
            {...register('cupo_por_dia', { valueAsNumber: true })}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            min={1}
          />
          {errors.cupo_por_dia && (
            <p className="mt-1 text-xs text-red-600">{errors.cupo_por_dia.message}</p>
          )}
        </div>
      </div>

      {crearMutation.isError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al crear la convocatoria.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={crearMutation.isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {crearMutation.isPending ? 'Guardando...' : 'Crear convocatoria'}
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
