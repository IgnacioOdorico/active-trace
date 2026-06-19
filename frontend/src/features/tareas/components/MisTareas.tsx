import { useMemo } from 'react'
import {
  useMisTareas,
  useCambiarEstadoTarea,
  useUsuariosAsignables,
  ESTADOS_WORKFLOW,
} from '../hooks/useTareasApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { formatNombreUsuario } from '../utils'
import type { Tarea, TareaEstado } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'
import { Button } from '../../../shared/components/ui/Button'

interface MisTareasProps {
  onVerDetalle: (tarea: Tarea) => void
  onEditar: (tarea: Tarea) => void
}

export default function MisTareas({ onVerDetalle, onEditar }: MisTareasProps) {
  const { data, isLoading, isError } = useMisTareas()
  const cambiarEstado = useCambiarEstadoTarea()
  const { data: asignables } = useUsuariosAsignables()
  const { data: materias } = useMaterias()

  const nombreUsuario = useMemo(() => {
    const mapa = new Map(asignables?.map((u) => [u.id, formatNombreUsuario(u)]))
    return (id: string) => mapa.get(id) ?? id
  }, [asignables])

  const nombreMateria = useMemo(() => {
    const mapa = new Map(materias?.map((m) => [m.id, m.nombre]))
    return (id: string) => mapa.get(id) ?? id
  }, [materias])

  if (isLoading) return <div className="py-8 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border">Cargando tareas...</div>
  if (isError) return <div className="py-8 text-center font-body-md text-on-error-container bg-error-container rounded neo-latex-border">Error al cargar tareas.</div>

  const tareas = data?.items ?? []

  if (tareas.length === 0) {
    return (
      <div className="rounded neo-latex-border bg-surface-container-lowest py-12 text-center font-body-md text-on-surface-variant">
        No tenés tareas asignadas.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {tareas.map((tarea) => {
        let badgeVariant: "neutral" | "primary" | "secondary" | "error" | "success" = "neutral"
        if (tarea.estado === 'Pendiente') badgeVariant = 'secondary'
        if (tarea.estado === 'En progreso') badgeVariant = 'primary'
        if (tarea.estado === 'Resuelta') badgeVariant = 'success'
        if (tarea.estado === 'Cancelada') badgeVariant = 'error'

        return (
          <div key={tarea.id} className="rounded neo-latex-border bg-surface-container-lowest p-5 hover:bg-surface-container transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="mb-2 flex items-center gap-3">
                  <Badge variant={badgeVariant}>
                    {tarea.estado}
                  </Badge>
                  {tarea.materia_id && (
                    <span className="font-body-md text-[12px] text-on-surface-variant">Materia: {nombreMateria(tarea.materia_id)}</span>
                  )}
                </div>
                <p className="font-body-md text-body-md font-medium text-on-surface">{tarea.descripcion}</p>
                <p className="mt-2 font-mono-data text-[12px] text-on-surface-variant">Asignado por: {nombreUsuario(tarea.asignado_por)}</p>
              </div>
              <div className="ml-6 flex flex-col items-end gap-3 min-w-[140px]">
                <select
                  value={tarea.estado}
                  onChange={(e) =>
                    cambiarEstado.mutate({ id: tarea.id, payload: { estado: e.target.value as TareaEstado } })
                  }
                  disabled={cambiarEstado.isPending}
                  className="w-full rounded neo-latex-border bg-surface-container-lowest px-2 py-1 font-mono-data text-[12px] text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  {ESTADOS_WORKFLOW.map((e) => (
                    <option key={e} value={e}>{e}</option>
                  ))}
                </select>
                <div className="flex gap-2">
                  <Button
                    onClick={() => onEditar(tarea)}
                    variant="ghost"
                  >
                    Editar
                  </Button>
                  <Button
                    onClick={() => onVerDetalle(tarea)}
                    variant="ghost"
                  >
                    Ver hilo
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
