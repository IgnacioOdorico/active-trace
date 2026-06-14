import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { vigenciaSchema, vigenciaMasivaSchema, type VigenciaFormData, type VigenciaMasivaFormData } from '../schemas'
import { useModificarVigencia, useModificarVigenciaMasiva, useMisEquipos } from '../hooks/useEquiposApi'
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
      vigencia_desde: equipo.vigencia_desde,
      vigencia_hasta: equipo.vigencia_hasta,
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
          <label className="mb-1 block text-xs font-medium text-gray-600">Desde</label>
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
          <label className="mb-1 block text-xs font-medium text-gray-600">Hasta</label>
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

  const { data: equiposData } = useMisEquipos()
  const mutation = useModificarVigenciaMasiva()
  const equipos = equiposData?.data ?? []

  const onSubmit = (values: VigenciaMasivaFormData) => {
    mutation.mutate(values, {
      onSuccess: (data) => {
        onSuccess(data.filas_afectadas)
        reset()
      },
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Equipo</label>
        <select
          {...register('equipo_origen_id')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">Seleccione un equipo</option>
          {equipos.map((eq) => (
            <option key={eq.id} value={eq.id}>
              {eq.materia_nombre} — {eq.cohorte}
            </option>
          ))}
        </select>
        {errors.equipo_origen_id && (
          <p className="mt-1 text-xs text-red-600">{errors.equipo_origen_id.message}</p>
        )}
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-600">Desde</label>
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
          <label className="mb-1 block text-xs font-medium text-gray-600">Hasta</label>
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
