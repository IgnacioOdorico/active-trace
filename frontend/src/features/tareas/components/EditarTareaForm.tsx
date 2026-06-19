import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { crearTareaSchema, type CrearTareaFormData } from '../schemas'
import { useEditarTarea, useUsuariosAsignables } from '../hooks/useTareasApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { formatNombreUsuario } from '../utils'
import type { Tarea } from '../types'
import { Button } from '../../../shared/components/ui/Button'

interface EditarTareaFormProps {
  tarea: Tarea
  onSuccess: () => void
  onCancel: () => void
}

export default function EditarTareaForm({ tarea, onSuccess, onCancel }: EditarTareaFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CrearTareaFormData>({
    resolver: zodResolver(crearTareaSchema),
    defaultValues: {
      descripcion: tarea.descripcion,
      asignado_a: tarea.asignado_a,
      materia_id: tarea.materia_id,
    },
  })

  const mutation = useEditarTarea()
  const { data: asignables, isLoading: asignablesLoading } = useUsuariosAsignables()
  const { data: materias, isLoading: materiasLoading } = useMaterias()

  const onSubmit = (values: CrearTareaFormData) => {
    mutation.mutate({ id: tarea.id, payload: values }, { onSuccess })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="mb-1 block font-label-caps text-label-caps text-on-surface-variant uppercase">Descripción</label>
        <textarea
          {...register('descripcion')}
          rows={3}
          className="w-full rounded neo-latex-border bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
        {errors.descripcion && (
          <p className="mt-1 font-body-md text-[12px] text-on-error-container">{errors.descripcion.message}</p>
        )}
      </div>

      <div>
        <label className="mb-1 block font-label-caps text-label-caps text-on-surface-variant uppercase">Asignado a</label>
        <select
          {...register('asignado_a')}
          disabled={asignablesLoading}
          className="w-full rounded neo-latex-border bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
        >
          <option value="" disabled>
            {asignablesLoading ? 'Cargando docentes...' : 'Seleccione un docente'}
          </option>
          {asignables?.map((u) => (
            <option key={u.id} value={u.id}>
              {formatNombreUsuario(u)} ({u.email})
            </option>
          ))}
        </select>
        {errors.asignado_a && (
          <p className="mt-1 font-body-md text-[12px] text-on-error-container">{errors.asignado_a.message}</p>
        )}
      </div>

      <div>
        <label className="mb-1 block font-label-caps text-label-caps text-on-surface-variant uppercase">
          Materia (opcional)
        </label>
        <select
          {...register('materia_id')}
          disabled={materiasLoading}
          className="w-full rounded neo-latex-border bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-50"
        >
          <option value="">
            {materiasLoading ? 'Cargando materias...' : 'Sin materia asociada'}
          </option>
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre}{m.comision ? ` - ${m.comision}` : ''}
            </option>
          ))}
        </select>
      </div>

      {mutation.isError && (
        <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">
          Error al editar la tarea.
        </div>
      )}

      <div className="flex gap-3 justify-end pt-2">
        <Button
          type="button"
          onClick={onCancel}
          variant="secondary"
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          disabled={mutation.isPending}
          variant="primary"
        >
          {mutation.isPending ? 'Guardando...' : 'Guardar cambios'}
        </Button>
      </div>
    </form>
  )
}
