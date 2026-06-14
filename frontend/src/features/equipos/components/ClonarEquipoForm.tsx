import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { clonarEquipoSchema, type ClonarEquipoFormData } from '../schemas'
import { useClonarEquipo, useMisEquipos } from '../hooks/useEquiposApi'

interface ClonarEquipoFormProps {
  onSuccess: () => void
}

export default function ClonarEquipoForm({ onSuccess }: ClonarEquipoFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ClonarEquipoFormData>({
    resolver: zodResolver(clonarEquipoSchema),
  })

  const { data: equiposData } = useMisEquipos()
  const mutation = useClonarEquipo()

  const onSubmit = (values: ClonarEquipoFormData) => {
    mutation.mutate(values, {
      onSuccess: () => {
        onSuccess()
        reset()
      },
    })
  }

  const equipos = equiposData?.data ?? []

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Equipo origen</label>
        <select
          {...register('equipo_origen_id')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">Seleccione un equipo</option>
          {equipos.map((eq) => (
            <option key={eq.id} value={eq.id}>
              {eq.materia_nombre} — {eq.cohorte} ({eq.rol})
            </option>
          ))}
        </select>
        {errors.equipo_origen_id && (
          <p className="mt-1 text-xs text-red-600">{errors.equipo_origen_id.message}</p>
        )}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Cohorte destino</label>
        <input
          {...register('cohorte_destino')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          placeholder="Ej: 2024-2"
        />
        {errors.cohorte_destino && (
          <p className="mt-1 text-xs text-red-600">{errors.cohorte_destino.message}</p>
        )}
      </div>

      {mutation.isSuccess && (
        <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">
          {mutation.data.ids_creados.length === 0
            ? 'No había asignaciones vigentes para clonar.'
            : `${mutation.data.ids_creados.length} asignaciones clonadas exitosamente.`}
        </div>
      )}

      {mutation.isError && (
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
