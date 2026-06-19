import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { salarioBaseSchema, type SalarioBaseFormValues } from '../schemas'
import { useCrearSalarioBase } from '../hooks/useGrillaSalarialApi'
import type { SalarioBase } from '../types'

interface Props {
  onSuccess: () => void
  initialValues?: SalarioBase
}

const ROLES = ['PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR']

export default function SalarioBaseForm({ onSuccess }: Props) {
  const { mutate, isPending } = useCrearSalarioBase()
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<SalarioBaseFormValues>({
    resolver: zodResolver(salarioBaseSchema),
  })

  function onSubmit(values: SalarioBaseFormValues) {
    mutate(
      { ...values, hasta: values.hasta || null },
      {
        onSuccess,
        onError: (err: unknown) => {
          const detail =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? ''
          setError('root', { message: `Error del servidor: ${detail}` })
        },
      },
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Rol *</label>
        <select
          {...register('rol')}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        >
          <option value="">Seleccioná un rol</option>
          {ROLES.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        {errors.rol && <p className="text-xs text-red-600">{errors.rol.message}</p>}
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Monto *</label>
        <input
          type="number"
          step="0.01"
          {...register('monto')}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          placeholder="0.00"
        />
        {errors.monto && <p className="text-xs text-red-600">{errors.monto.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Desde *</label>
          <input
            type="date"
            {...register('desde')}
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          {errors.desde && <p className="text-xs text-red-600">{errors.desde.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Hasta</label>
          <input
            type="date"
            {...register('hasta')}
            className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          {errors.hasta && <p className="text-xs text-red-600">{errors.hasta.message}</p>}
        </div>
      </div>

      {errors.root && (
        <p className="rounded bg-red-50 p-2 text-xs text-red-700">{errors.root.message}</p>
      )}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isPending ? 'Guardando...' : 'Guardar salario base'}
        </button>
      </div>
    </form>
  )
}
