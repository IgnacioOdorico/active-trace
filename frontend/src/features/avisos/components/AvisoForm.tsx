import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { avisoSchema, type AvisoFormData } from '../schemas'
import { useCrearAviso, useEditarAviso } from '../hooks/useAvisosApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'
import type { Aviso } from '../types'

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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label htmlFor="aviso-alcance" className="mb-1 block text-sm font-medium text-gray-700">
            Alcance
          </label>
          <select
            id="aviso-alcance"
            {...register('alcance')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="Global">Global</option>
            <option value="PorMateria">Por materia</option>
            <option value="PorCohorte">Por cohorte</option>
            <option value="PorRol">Por rol</option>
          </select>
          {errors.alcance && <p className="mt-1 text-xs text-red-600">{errors.alcance.message}</p>}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Severidad</label>
          <select
            {...register('severidad')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          >
            <option value="Info">Info</option>
            <option value="Advertencia">Advertencia</option>
            <option value="Crítico">Crítico</option>
          </select>
        </div>
      </div>

      {alcance === 'PorMateria' && (
        <div>
          <label htmlFor="aviso-materia" className="mb-1 block text-sm font-medium text-gray-700">
            Materia
          </label>
          <select
            id="aviso-materia"
            {...register('materia_id')}
            disabled={materiasLoading}
            defaultValue=""
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
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
            <p className="mt-1 text-xs text-red-600">{errors.materia_id.message}</p>
          )}
        </div>
      )}

      {alcance === 'PorCohorte' && (
        <div>
          <label htmlFor="aviso-cohorte" className="mb-1 block text-sm font-medium text-gray-700">
            Cohorte
          </label>
          <select
            id="aviso-cohorte"
            {...register('cohorte_id')}
            disabled={cohortesLoading}
            defaultValue=""
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
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
            <p className="mt-1 text-xs text-red-600">{errors.cohorte_id.message}</p>
          )}
        </div>
      )}

      {alcance === 'PorRol' && (
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Rol destino</label>
          <select
            {...register('rol_destino')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
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

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Título</label>
        <input
          {...register('titulo')}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        {errors.titulo && <p className="mt-1 text-xs text-red-600">{errors.titulo.message}</p>}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Cuerpo</label>
        <textarea
          {...register('cuerpo')}
          rows={4}
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
        />
        {errors.cuerpo && <p className="mt-1 text-xs text-red-600">{errors.cuerpo.message}</p>}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Vigencia inicio</label>
          <input
            type="datetime-local"
            {...register('inicio_en')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.inicio_en && (
            <p className="mt-1 text-xs text-red-600">{errors.inicio_en.message}</p>
          )}
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Vigencia fin</label>
          <input
            type="datetime-local"
            {...register('fin_en')}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
          />
          {errors.fin_en && (
            <p className="mt-1 text-xs text-red-600">{errors.fin_en.message}</p>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Orden</label>
          <input
            type="number"
            {...register('orden', { valueAsNumber: true })}
            className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm"
            min={0}
          />
        </div>
        <div className="flex flex-col gap-2 pt-6">
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" {...register('activo')} />
            Activo
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input type="checkbox" {...register('requiere_ack')} />
            Requiere confirmación de lectura
          </label>
        </div>
      </div>

      {(crearMutation.isError || editarMutation.isError) && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al guardar el aviso. Intente nuevamente.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isPending ? 'Guardando...' : aviso ? 'Actualizar aviso' : 'Crear aviso'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
