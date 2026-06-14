import { useMisTareas, useCambiarEstadoTarea, ESTADOS_WORKFLOW } from '../hooks/useTareasApi'
import type { Tarea, TareaEstado } from '../types'

const ESTADO_COLORS: Record<TareaEstado, string> = {
  Pendiente: 'bg-gray-100 text-gray-700',
  'En progreso': 'bg-blue-100 text-blue-700',
  Resuelta: 'bg-green-100 text-green-700',
  Cancelada: 'bg-red-100 text-red-700',
}

interface MisTareasProps {
  onVerDetalle: (tarea: Tarea) => void
}

export default function MisTareas({ onVerDetalle }: MisTareasProps) {
  const { data, isLoading, isError } = useMisTareas()
  const cambiarEstado = useCambiarEstadoTarea()

  if (isLoading) return <div className="py-8 text-center text-gray-500">Cargando tareas...</div>
  if (isError) return <div className="py-8 text-center text-red-600">Error al cargar tareas.</div>

  const tareas = data?.data ?? []

  if (tareas.length === 0) {
    return (
      <div className="rounded-lg bg-gray-50 py-12 text-center text-gray-500">
        No tenés tareas asignadas.
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {tareas.map((tarea) => (
        <div key={tarea.id} className="rounded-lg border border-gray-200 bg-white p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="mb-1 flex items-center gap-2">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ESTADO_COLORS[tarea.estado]}`}>
                  {tarea.estado}
                </span>
                {tarea.materia_nombre && (
                  <span className="text-xs text-gray-500">{tarea.materia_nombre}</span>
                )}
              </div>
              <p className="font-medium text-gray-900">{tarea.titulo}</p>
              <p className="mt-1 text-sm text-gray-600">{tarea.descripcion}</p>
              <p className="mt-1 text-xs text-gray-400">Asignado por: {tarea.asignador_nombre}</p>
            </div>
            <div className="ml-4 flex flex-col gap-2">
              <select
                value={tarea.estado}
                onChange={(e) =>
                  cambiarEstado.mutate({ id: tarea.id, payload: { estado: e.target.value as TareaEstado } })
                }
                disabled={cambiarEstado.isPending}
                className="rounded-md border border-gray-300 px-2 py-1 text-xs"
              >
                {ESTADOS_WORKFLOW.map((e) => (
                  <option key={e} value={e}>{e}</option>
                ))}
              </select>
              <button
                type="button"
                onClick={() => onVerDetalle(tarea)}
                className="text-xs text-blue-600 hover:underline"
              >
                Ver comentarios
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
