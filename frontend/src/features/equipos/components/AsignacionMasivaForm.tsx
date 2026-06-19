import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { asignacionMasivaSchema, ROLES_EQUIPO, type AsignacionMasivaFormData } from '../schemas'
import { useAsignacionMasiva, useDocentesDisponibles } from '../hooks/useEquiposApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCarreras, useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'

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
  const { data: docentes, isLoading: docentesLoading } = useDocentesDisponibles()
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const { data: carreras, isLoading: carrerasLoading } = useCarreras()
  const { data: cohortes, isLoading: cohortesLoading } = useCohortes()

  const onSubmit = (values: AsignacionMasivaFormData) => {
    mutation.mutate({ ...values, hasta: values.hasta || undefined }, {
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
        <label htmlFor="usuario_ids" className="mb-1 block text-sm font-medium text-gray-700">
          Docentes
        </label>
        <select
          id="usuario_ids"
          multiple
          {...register('usuario_ids')}
          className="h-32 w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          {docentesLoading && <option disabled>Cargando docentes...</option>}
          {docentes?.map((d) => (
            <option key={d.id} value={d.id}>
              {d.nombre_completo} ({d.roles.join(', ')})
            </option>
          ))}
        </select>
        {errors.usuario_ids && (
          <p className="mt-1 text-xs text-red-600">{errors.usuario_ids.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="materia_id" className="mb-1 block text-sm font-medium text-gray-700">Materia</label>
          <select
            id="materia_id"
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
        <div>
          <label htmlFor="carrera_id" className="mb-1 block text-sm font-medium text-gray-700">Carrera</label>
          <select
            id="carrera_id"
            {...register('carrera_id')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Seleccione una carrera</option>
            {carrerasLoading && <option disabled>Cargando carreras...</option>}
            {carreras?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
          {errors.carrera_id && (
            <p className="mt-1 text-xs text-red-600">{errors.carrera_id.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="cohorte_id" className="mb-1 block text-sm font-medium text-gray-700">Cohorte</label>
          <select
            id="cohorte_id"
            {...register('cohorte_id')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Seleccione una cohorte</option>
            {cohortesLoading && <option disabled>Cargando cohortes...</option>}
            {cohortes?.map((c) => (
              <option key={c.id} value={c.id}>{c.nombre}</option>
            ))}
          </select>
          {errors.cohorte_id && (
            <p className="mt-1 text-xs text-red-600">{errors.cohorte_id.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="rol" className="mb-1 block text-sm font-medium text-gray-700">Rol</label>
          <select
            id="rol"
            {...register('rol')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="">Seleccione rol</option>
            {ROLES_EQUIPO.map((rol) => (
              <option key={rol} value={rol}>{rol}</option>
            ))}
          </select>
          {errors.rol && <p className="mt-1 text-xs text-red-600">{errors.rol.message}</p>}
        </div>
        <div>
          <label htmlFor="desde" className="mb-1 block text-sm font-medium text-gray-700">Vigencia desde</label>
          <input
            id="desde"
            type="date"
            {...register('desde')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.desde && (
            <p className="mt-1 text-xs text-red-600">{errors.desde.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="hasta" className="mb-1 block text-sm font-medium text-gray-700">Vigencia hasta (opcional)</label>
          <input
            id="hasta"
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
          Asignación masiva completada. {mutation.data?.ids_creados.length} asignaciones creadas.
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
