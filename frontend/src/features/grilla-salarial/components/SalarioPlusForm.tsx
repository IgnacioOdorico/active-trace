import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { salarioPlusSchema, type SalarioPlusFormValues } from '../schemas'
import { useCrearSalarioPlus } from '../hooks/useGrillaSalarialApi'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

interface Props {
  onSuccess: () => void
}

const ROLES = ['PROFESOR', 'TUTOR', 'NEXO', 'COORDINADOR']

export default function SalarioPlusForm({ onSuccess }: Props) {
  const { mutate, isPending } = useCrearSalarioPlus()
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors },
  } = useForm<SalarioPlusFormValues>({
    resolver: zodResolver(salarioPlusSchema),
  })

  function onSubmit(values: SalarioPlusFormValues) {
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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Grupo *</label>
          <Input
            type="text"
            {...register('grupo')}
            className="w-full"
            placeholder="Ej: PROG, BD"
          />
          {errors.grupo && <p className="mt-1 font-body-md text-[12px] text-error">{errors.grupo.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Rol *</label>
          <select
            {...register('rol')}
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">Seleccioná un rol</option>
            {ROLES.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          {errors.rol && <p className="mt-1 font-body-md text-[12px] text-error">{errors.rol.message}</p>}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Monto *</label>
        <Input
          type="number"
          step="0.01"
          {...register('monto')}
          className="w-full"
          placeholder="0.00"
        />
        {errors.monto && <p className="mt-1 font-body-md text-[12px] text-error">{errors.monto.message}</p>}
      </div>

      <div className="flex flex-col gap-1">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Descripción *</label>
        <Input
          type="text"
          {...register('descripcion')}
          className="w-full"
          placeholder="Describí el plus"
        />
        {errors.descripcion && (
          <p className="mt-1 font-body-md text-[12px] text-error">{errors.descripcion.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Desde *</label>
          <Input
            type="date"
            {...register('desde')}
            className="w-full"
          />
          {errors.desde && <p className="mt-1 font-body-md text-[12px] text-error">{errors.desde.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Hasta</label>
          <Input
            type="date"
            {...register('hasta')}
            className="w-full"
          />
          {errors.hasta && <p className="mt-1 font-body-md text-[12px] text-error">{errors.hasta.message}</p>}
        </div>
      </div>

      {errors.root && (
        <p className="rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">{errors.root.message}</p>
      )}

      <div className="flex justify-end pt-4 border-t border-outline-variant">
        <Button
          type="submit"
          disabled={isPending}
          variant="primary"
        >
          {isPending ? 'Guardando...' : 'Guardar salario plus'}
        </Button>
      </div>
    </form>
  )
}
