import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { vigenciaSchema, vigenciaMasivaSchema, type VigenciaFormData, type VigenciaMasivaFormData } from '../schemas'
import { useModificarVigencia, useModificarVigenciaMasiva } from '../hooks/useEquiposApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'
import type { MiEquipo } from '../types'

interface VigenciaFormProps {
  equipo: MiEquipo
  onSuccess: () => void
}

export function VigenciaIndividualForm({ equipo, onSuccess }: VigenciaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<VigenciaFormData>({
    resolver: zodResolver(vigenciaSchema),
    defaultValues: {
      desde: equipo.vigencia_desde,
      hasta: equipo.vigencia_hasta,
    },
  })

  const mutation = useModificarVigencia()

  const onSubmit = (values: VigenciaFormData) => {
    mutation.mutate(
      { id: equipo.id, payload: values },
      { onSuccess: () => onSuccess() },
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <p className="text-sm font-medium text-gray-700">
        Equipo: {equipo.materia_nombre} — {equipo.rol}
      </p>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="vi-desde" className="mb-1 block text-xs font-medium text-gray-600">Desde</label>
          <input
            id="vi-desde"
            type="date"
            {...register('desde')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.desde && (
            <p className="mt-1 text-xs text-red-600">{errors.desde.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="vi-hasta" className="mb-1 block text-xs font-medium text-gray-600">Hasta</label>
          <input
            id="vi-hasta"
            type="date"
            {...register('hasta')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.hasta && (
            <p className="mt-1 text-xs text-red-600">{errors.hasta.message}</p>
          )}
        </div>
      </div>
      {mutation.isSuccess && (
        <p className="text-sm text-green-700">Vigencia actualizada.</p>
      )}
      <button
        type="submit"
        disabled={mutation.isPending}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {mutation.isPending ? 'Guardando...' : 'Guardar vigencia'}
      </button>
    </form>
  )
}

interface VigenciaMasivaFormProps {
  onSuccess: (filasAfectadas: number) => void
}

export function VigenciaMasivaForm({ onSuccess }: VigenciaMasivaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<VigenciaMasivaFormData>({
    resolver: zodResolver(vigenciaMasivaSchema),
  })

  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const { data: cohortes, isLoading: cohortesLoading } = useCohortes()
  const mutation = useModificarVigenciaMasiva()

  const onSubmit = (values: VigenciaMasivaFormData) => {
    mutation.mutate({ ...values, hasta: values.hasta || undefined }, {
      onSuccess: (data) => {
        onSuccess(data.filas_afectadas)
        reset()
      },
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="vm-materia_id" className="mb-1 block text-sm font-medium text-gray-700">Materia</label>
          <select
            id="vm-materia_id"
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
          <label htmlFor="vm-cohorte_id" className="mb-1 block text-sm font-medium text-gray-700">Cohorte</label>
          <select
            id="vm-cohorte_id"
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
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="vm-desde" className="mb-1 block text-xs font-medium text-gray-600">Desde</label>
          <input
            id="vm-desde"
            type="date"
            {...register('desde')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.desde && (
            <p className="mt-1 text-xs text-red-600">{errors.desde.message}</p>
          )}
        </div>
        <div>
          <label htmlFor="vm-hasta" className="mb-1 block text-xs font-medium text-gray-600">Hasta (opcional)</label>
          <input
            id="vm-hasta"
            type="date"
            {...register('hasta')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.hasta && (
            <p className="mt-1 text-xs text-red-600">{errors.hasta.message}</p>
          )}
        </div>
      </div>
      {mutation.isSuccess && (
        <p className="text-sm text-green-700">
          {mutation.data.filas_afectadas} fila(s) afectada(s).
        </p>
      )}
      <button
        type="submit"
        disabled={mutation.isPending}
        className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {mutation.isPending ? 'Actualizando...' : 'Actualizar vigencia masiva'}
      </button>
    </form>
  )
}
