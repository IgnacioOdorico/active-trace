import { useMemo, useState } from 'react'
import {
  useTareasAdmin,
  useCambiarEstadoTarea,
  useUsuariosAsignables,
  ESTADOS_WORKFLOW,
} from '../hooks/useTareasApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { formatNombreUsuario } from '../utils'
import type { Tarea, TareasAdminFilters, TareaEstado } from '../types'
import { Badge } from '../../../shared/components/ui/Badge'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

interface TareasAdminProps {
  onVerDetalle: (tarea: Tarea) => void
  onEditar: (tarea: Tarea) => void
}

export default function TareasAdmin({ onVerDetalle, onEditar }: TareasAdminProps) {
  const [filters, setFilters] = useState<TareasAdminFilters>({})
  const { data, isLoading, isError } = useTareasAdmin(filters)
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

  const handleFilter = (key: keyof TareasAdminFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }))
  }

  if (isLoading) return <div className="py-8 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border mt-4">Cargando tareas...</div>
  if (isError) return <div className="py-8 text-center font-body-md text-on-error-container bg-error-container rounded neo-latex-border mt-4">Error al cargar tareas.</div>

  const tareas = data?.items ?? []

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-4 rounded neo-latex-border bg-surface-container p-4">
        <div className="w-[200px]">
          <Input
            type="text"
            placeholder="Buscar..."
            onChange={(e) => handleFilter('busqueda', e.target.value)}
          />
        </div>
        <div className="w-[160px]">
          <Input
            type="text"
            placeholder="ID asignado"
            onChange={(e) => handleFilter('asignado_a', e.target.value)}
          />
        </div>
        <div className="w-[160px]">
          <Input
            type="text"
            placeholder="ID asignador"
            onChange={(e) => handleFilter('asignado_por', e.target.value)}
          />
        </div>
        <div className="w-[200px]">
          <select
            className="w-full rounded neo-latex-border bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            onChange={(e) => handleFilter('estado', e.target.value)}
          >
            <option value="">Todos los estados</option>
            {ESTADOS_WORKFLOW.map((e) => (
              <option key={e} value={e}>{e}</option>
            ))}
          </select>
        </div>
      </div>

      {tareas.length === 0 ? (
        <div className="rounded neo-latex-border bg-surface-container-lowest py-12 text-center font-body-md text-on-surface-variant">
          No se encontraron tareas.
        </div>
      ) : (
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
                    <p className="mt-2 font-mono-data text-[12px] text-on-surface-variant">
                      {nombreUsuario(tarea.asignado_por)} → {nombreUsuario(tarea.asignado_a)}
                    </p>
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
      )}
    </div>
  )
}
