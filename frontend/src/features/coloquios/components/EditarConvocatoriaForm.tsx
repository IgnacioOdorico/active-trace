import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { editarConvocatoriaSchema, type EditarConvocatoriaFormData } from '../schemas'
import { useEditarConvocatoria } from '../hooks/useColoquiosApi'
import type { Convocatoria } from '../types'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <p className="font-body-md text-[12px] text-on-surface-variant">
        Materia y cohorte no se pueden modificar una vez creada la convocatoria.
      </p>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="editar-tipo" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Tipo
          </label>
          <select
            id="editar-tipo"
            {...register('tipo')}
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            {TIPOS_EVALUACION.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
          {errors.tipo && <p className="mt-1 font-body-md text-[12px] text-error">{errors.tipo.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Instancia</label>
          <Input
            {...register('instancia')}
            className="w-full"
          />
          {errors.instancia && (
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.instancia.message}</p>
          )}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <label htmlFor="editar-dias" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
          Cantidad de días a generar
        </label>
        <Input
          id="editar-dias"
          type="number"
          {...register('dias_disponibles', { valueAsNumber: true })}
          className="w-full max-w-xs"
          min={1}
        />
        {errors.dias_disponibles && (
          <p className="mt-1 font-body-md text-[12px] text-error">{errors.dias_disponibles.message}</p>
        )}
      </div>

      {editarMutation.isError && (
        <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">
          Error al actualizar la convocatoria.
        </div>
      )}

      <div className="flex gap-3 pt-4 border-t border-outline-variant">
        <Button
          type="submit"
          disabled={editarMutation.isPending}
          variant="primary"
        >
          {editarMutation.isPending ? 'Guardando...' : 'Actualizar convocatoria'}
        </Button>
        <Button
          type="button"
          onClick={onCancel}
          variant="secondary"
        >
          Cancelar
        </Button>
      </div>
    </form>
  )
}
