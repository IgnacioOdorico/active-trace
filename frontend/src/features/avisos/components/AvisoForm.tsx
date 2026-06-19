import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { avisoSchema, type AvisoFormData } from '../schemas'
import { useCrearAviso, useEditarAviso } from '../hooks/useAvisosApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'
import type { Aviso } from '../types'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

interface AvisoFormProps {
  aviso?: Aviso
  onSuccess: () => void
  onCancel: () => void
}

export default function AvisoForm({ aviso, onSuccess, onCancel }: AvisoFormProps) {
  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<AvisoFormData>({
    resolver: zodResolver(avisoSchema),
    defaultValues: aviso
      ? {
          alcance: aviso.alcance,
          materia_id: aviso.materia_id,
          cohorte_id: aviso.cohorte_id,
          rol_destino: aviso.rol_destino,
          severidad: aviso.severidad,
          titulo: aviso.titulo,
          cuerpo: aviso.cuerpo,
          inicio_en: aviso.inicio_en,
          fin_en: aviso.fin_en,
          orden: aviso.orden,
          activo: aviso.activo,
          requiere_ack: aviso.requiere_ack,
        }
      : { alcance: 'Global', severidad: 'Info', orden: 0, activo: true, requiere_ack: false },
  })

  const alcance = watch('alcance')
  const crearMutation = useCrearAviso()
  const editarMutation = useEditarAviso()
  const isPending = crearMutation.isPending || editarMutation.isPending
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const { data: cohortes, isLoading: cohortesLoading } = useCohortes()

  const onSubmit = (values: AvisoFormData) => {
    if (aviso) {
      editarMutation.mutate({ id: aviso.id, payload: values }, { onSuccess })
    } else {
      crearMutation.mutate(values, { onSuccess })
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="aviso-alcance" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Alcance
          </label>
          <select
            id="aviso-alcance"
            {...register('alcance')}
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="Global">Global</option>
            <option value="PorMateria">Por materia</option>
            <option value="PorCohorte">Por cohorte</option>
            <option value="PorRol">Por rol</option>
          </select>
          {errors.alcance && <p className="mt-1 font-body-md text-[12px] text-error">{errors.alcance.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Severidad</label>
          <select
            {...register('severidad')}
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="Info">Info</option>
            <option value="Advertencia">Advertencia</option>
            <option value="Crítico">Crítico</option>
          </select>
        </div>
      </div>

      {alcance === 'PorMateria' && (
        <div className="flex flex-col gap-1">
          <label htmlFor="aviso-materia" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Materia
          </label>
          <select
            id="aviso-materia"
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
      )}

      {alcance === 'PorCohorte' && (
        <div className="flex flex-col gap-1">
          <label htmlFor="aviso-cohorte" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Cohorte
          </label>
          <select
            id="aviso-cohorte"
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
      )}

      {alcance === 'PorRol' && (
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Rol destino</label>
          <select
            {...register('rol_destino')}
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">— Seleccionar —</option>
            <option value="ALUMNO">Alumno</option>
            <option value="TUTOR">Tutor</option>
            <option value="PROFESOR">Profesor</option>
            <option value="COORDINADOR">Coordinador</option>
            <option value="NEXO">Nexo</option>
            <option value="ADMIN">Admin</option>
            <option value="FINANZAS">Finanzas</option>
          </select>
        </div>
      )}

      <div className="flex flex-col gap-1">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Título</label>
        <Input
          {...register('titulo')}
          className="w-full"
        />
        {errors.titulo && <p className="mt-1 font-body-md text-[12px] text-error">{errors.titulo.message}</p>}
      </div>

      <div className="flex flex-col gap-1">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Cuerpo</label>
        <textarea
          {...register('cuerpo')}
          rows={4}
          className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
        {errors.cuerpo && <p className="mt-1 font-body-md text-[12px] text-error">{errors.cuerpo.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Vigencia inicio</label>
          <Input
            type="datetime-local"
            {...register('inicio_en')}
            className="w-full"
          />
          {errors.inicio_en && (
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.inicio_en.message}</p>
          )}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Vigencia fin</label>
          <Input
            type="datetime-local"
            {...register('fin_en')}
            className="w-full"
          />
          {errors.fin_en && (
            <p className="mt-1 font-body-md text-[12px] text-error">{errors.fin_en.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Orden</label>
          <Input
            type="number"
            {...register('orden', { valueAsNumber: true })}
            className="w-full"
            min={0}
          />
        </div>
        <div className="flex flex-col gap-3 pt-6">
          <label className="flex items-center gap-2 font-body-md text-on-surface">
            <input type="checkbox" {...register('activo')} className="rounded border-outline-variant text-primary focus:ring-primary" />
            Activo
          </label>
          <label className="flex items-center gap-2 font-body-md text-on-surface">
            <input type="checkbox" {...register('requiere_ack')} className="rounded border-outline-variant text-primary focus:ring-primary" />
            Requiere confirmación de lectura
          </label>
        </div>
      </div>

      {(crearMutation.isError || editarMutation.isError) && (
        <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">
          Error al guardar el aviso. Intente nuevamente.
        </div>
      )}

      <div className="flex gap-3 pt-4 border-t border-outline-variant">
        <Button
          type="submit"
          disabled={isPending}
          variant="primary"
        >
          {isPending ? 'Guardando...' : aviso ? 'Actualizar aviso' : 'Crear aviso'}
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
