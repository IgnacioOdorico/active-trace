import { useState } from 'react'
import { useTareasAdmin, useCambiarEstadoTarea, ESTADOS_WORKFLOW } from '../hooks/useTareasApi'
import type { Tarea, TareasAdminFilters, TareaEstado } from '../types'

const ESTADO_COLORS: Record<TareaEstado, string> = {
  Pendiente: 'bg-gray-100 text-gray-700',
  'En progreso': 'bg-blue-100 text-blue-700',
  Resuelta: 'bg-green-100 text-green-700',
  Cancelada: 'bg-red-100 text-red-700',
}

interface TareasAdminProps {
  onVerDetalle: (tarea: Tarea) => void
}

export default function TareasAdmin({ onVerDetalle }: TareasAdminProps) {
  const [filters, setFilters] = useState<TareasAdminFilters>({})
  const { data, isLoading, isError } = useTareasAdmin(filters)
  const cambiarEstado = useCambiarEstadoTarea()

  const handleFilter = (key: keyof TareasAdminFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }))
  }

  if (isLoading) return <div className="py-8 text-center text-gray-500">Cargando tareas...</div>
  if (isError) return <div className="py-8 text-center text-red-600">Error al cargar tareas.</div>

  const tareas = data?.data ?? []

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Buscar..."
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('q', e.target.value)}
        />
        <input
          type="text"
          placeholder="ID asignado"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('asignado_id', e.target.value)}
        />
        <input
          type="text"
          placeholder="ID asignador"
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('asignador_id', e.target.value)}
        />
        <select
          className="rounded-md border border-gray-300 px-3 py-2 text-sm"
          onChange={(e) => handleFilter('estado', e.target.value)}
        >
          <option value="">Todos los estados</option>
          {ESTADOS_WORKFLOW.map((e) => (
            <option key={e} value={e}>{e}</option>
          ))}
        </select>
      </div>

      {tareas.length === 0 ? (
        <div className="rounded-lg bg-gray-50 py-12 text-center text-gray-500">
          No se encontraron tareas.
        </div>
      ) : (
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
                  <p className="mt-1 text-xs text-gray-400">
                    {tarea.asignador_nombre} → {tarea.asignado_nombre}
                  </p>
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
                    Comentarios
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
