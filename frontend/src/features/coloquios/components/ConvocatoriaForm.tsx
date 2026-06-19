import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { crearConvocatoriaSchema, type CrearConvocatoriaFormData } from '../schemas'
import { useCrearConvocatoria } from '../hooks/useColoquiosApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="convocatoria-materia" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Materia
          </label>
          <select
            id="convocatoria-materia"
            {...register('materia_id')}
            disabled={materiasLoading}
            defaultValue=""
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.materia_id.message}</p>
          )}
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="convocatoria-cohorte" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Cohorte
          </label>
          <select
            id="convocatoria-cohorte"
            {...register('cohorte_id')}
            disabled={cohortesLoading}
            defaultValue=""
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.cohorte_id.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="convocatoria-tipo" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Tipo
          </label>
          <select
            id="convocatoria-tipo"
            {...register('tipo')}
            defaultValue=""
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
          {errors.tipo && <p className="mt-1 font-body-md text-[12px] text-error">{errors.tipo.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Instancia</label>
          <Input
            {...register('instancia')}
            className="w-full"
            placeholder="Ej: Primer llamado"
          />
          {errors.instancia && (
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.instancia.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="convocatoria-dias" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Cantidad de días a generar
          </label>
          <Input
            id="convocatoria-dias"
            type="number"
            {...register('dias_disponibles', { valueAsNumber: true })}
            className="w-full"
            min={1}
          />
          <p className="mt-1 font-body-md text-[12px] text-on-surface-variant">
            Se generan turnos a partir de mañana, uno por cada día corrido.
          </p>
          {errors.dias_disponibles && (
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.dias_disponibles.message}</p>
          )}
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="convocatoria-cupo" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Cupo por día
          </label>
          <Input
            id="convocatoria-cupo"
            type="number"
            {...register('cupo_por_dia', { valueAsNumber: true })}
            className="w-full"
            min={1}
          />
          {errors.cupo_por_dia && (
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.cupo_por_dia.message}</p>
          )}
        </div>
      </div>

      {crearMutation.isError && (
        <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">
          Error al crear la convocatoria.
        </div>
      )}

      <div className="flex gap-3 pt-4 border-t border-outline-variant">
        <Button
          type="submit"
          disabled={crearMutation.isPending}
          variant="primary"
        >
          {crearMutation.isPending ? 'Guardando...' : 'Crear convocatoria'}
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
