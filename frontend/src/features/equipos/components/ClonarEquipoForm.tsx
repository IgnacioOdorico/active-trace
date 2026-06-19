import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { clonarEquipoSchema, type ClonarEquipoFormData } from '../schemas'
import { useClonarEquipo } from '../hooks/useEquiposApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'

interface ClonarEquipoFormProps {
  onSuccess: () => void
}

export default function ClonarEquipoForm({ onSuccess }: ClonarEquipoFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setError,
  } = useForm<ClonarEquipoFormData>({
    resolver: zodResolver(clonarEquipoSchema),
  })

  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const { data: cohortes, isLoading: cohortesLoading } = useCohortes()
  const mutation = useClonarEquipo()

  const onSubmit = (values: ClonarEquipoFormData) => {
    mutation.mutate({ ...values, hasta: values.hasta || undefined }, {
      onSuccess: () => {
        onSuccess()
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
        <label htmlFor="clonar-materia_id" className="mb-1 block text-sm font-medium text-gray-700">
          Materia
        </label>
        <select
          id="clonar-materia_id"
          {...register('materia_id')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">Seleccione una materia</option>
          {materiasLoading && <option disabled>Cargando materias...</option>}
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>{m.nombre}</option>
          ))}
        </select>
        {errors.materia_id && (
          <p className="mt-1 text-xs text-red-600">{errors.materia_id.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="cohorte_origen_id" className="mb-1 block text-sm font-medium text-gray-700">
            Cohorte origen
          </label>
          <select
            id="cohorte_origen_id"
            {...register('cohorte_origen_id')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Seleccione la cohorte origen</option>
            {cohortesLoading && <option disabled>Cargando cohortes...</option>}
            {cohortes?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
          {errors.cohorte_origen_id && (
            <p className="mt-1 text-xs text-red-600">{errors.cohorte_origen_id.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="cohorte_destino_id" className="mb-1 block text-sm font-medium text-gray-700">
            Cohorte destino
          </label>
          <select
            id="cohorte_destino_id"
            {...register('cohorte_destino_id')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Seleccione la cohorte destino</option>
            {cohortesLoading && <option disabled>Cargando cohortes...</option>}
            {cohortes?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
          {errors.cohorte_destino_id && (
            <p className="mt-1 text-xs text-red-600">{errors.cohorte_destino_id.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="clonar-desde" className="mb-1 block text-sm font-medium text-gray-700">
            Vigencia desde
          </label>
          <input
            id="clonar-desde"
            type="date"
            {...register('desde')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.desde && (
            <p className="mt-1 text-xs text-red-600">{errors.desde.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="clonar-hasta" className="mb-1 block text-sm font-medium text-gray-700">
            Vigencia hasta (opcional)
          </label>
          <input
            id="clonar-hasta"
            type="date"
            {...register('hasta')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.hasta && (
            <p className="mt-1 text-xs text-red-600">{errors.hasta.message}</p>
          )}
        </div>
      </div>

      {errors.root && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">{errors.root.message}</div>
      )}

      {mutation.isSuccess && (
        <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">
          {mutation.data.ids_creados.length === 0
            ? 'No había asignaciones vigentes para clonar.'
            : `${mutation.data.ids_creados.length} asignaciones clonadas exitosamente.`}
        </div>
      )}

      {mutation.isError && !errors.root && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al clonar el equipo. Intente nuevamente.
        </div>
      )}

      <button
        type="submit"
        disabled={mutation.isPending}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {mutation.isPending ? 'Clonando...' : 'Clonar equipo'}
      </button>
    </form>
  )
}
