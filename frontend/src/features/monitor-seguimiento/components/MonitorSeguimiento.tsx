import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useMonitorSeguimiento } from '../hooks/useMonitoresApi'

export default function MonitorSeguimiento() {
  const { user } = useAuth()
  const { data: materias } = useMaterias()
  const isCoordinador = user?.roles.includes('coordinador')

  const [materiaId, setMateriaId] = useState('')
  const [alumnoId, setAlumnoId] = useState('')
  const [alumnoBusqueda, setAlumnoBusqueda] = useState('')
  const [actividadMinima, setActividadMinima] = useState('')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [pagina, setPagina] = useState(1)

  const { data, isLoading, isError } = useMonitorSeguimiento({
    materia_id: isCoordinador ? (materiaId || undefined) : undefined,
    alumno_id: alumnoId || undefined,
    actividad_minima: actividadMinima || undefined,
    fecha_desde: isCoordinador ? (fechaDesde || undefined) : undefined,
    fecha_hasta: isCoordinador ? (fechaHasta || undefined) : undefined,
    pagina,
    por_pagina: 50,
  })

  const totalPaginas = data ? Math.ceil(data.total / data.por_pagina) : 0

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div>
          <label htmlFor="seg-materia" className="block text-xs font-medium text-gray-700">Materia</label>
          <select
            id="seg-materia"
            value={materiaId}
            onChange={(e) => { setMateriaId(e.target.value); setPagina(1) }}
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            {isCoordinador ? (
              <>
                <option value="">{materias && materias.length > 0 ? 'Todas las materias' : 'Cargando materias...'}</option>
                {materias?.map((m) => (
                  <option key={m.id} value={m.id}>{m.nombre}</option>
                ))}
              </>
            ) : (
              <>
                <option value="">{materias && materias.length > 0 ? 'Mis materias' : 'Cargando materias...'}</option>
                {materias?.map((m) => (
                  <option key={m.id} value={m.id}>{m.nombre}</option>
                ))}
              </>
            )}
          </select>
          {!isCoordinador && (
            <p className="mt-1 text-xs text-gray-400">Solo sus materias asignadas</p>
          )}
        </div>

        <div>
          <label htmlFor="seg-alumno" className="block text-xs font-medium text-gray-700">Alumno</label>
          <input
            id="seg-alumno"
            type="text"
            value={alumnoBusqueda}
            onChange={(e) => setAlumnoBusqueda(e.target.value)}
            placeholder="Nombre del alumno"
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="seg-actividad" className="block text-xs font-medium text-gray-700">
            Actividad mínima
          </label>
          <input
            id="seg-actividad"
            type="text"
            value={actividadMinima}
            onChange={(e) => { setActividadMinima(e.target.value); setPagina(1) }}
            placeholder="Ej: TP1"
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        {isCoordinador && (
          <>
            <div>
              <label htmlFor="seg-fecha-desde" className="block text-xs font-medium text-gray-700">Fecha desde</label>
              <input
                id="seg-fecha-desde"
                type="date"
                value={fechaDesde}
                onChange={(e) => { setFechaDesde(e.target.value); setPagina(1) }}
                className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
            <div>
              <label htmlFor="seg-fecha-hasta" className="block text-xs font-medium text-gray-700">Fecha hasta</label>
              <input
                id="seg-fecha-hasta"
                type="date"
                value={fechaHasta}
                onChange={(e) => { setFechaHasta(e.target.value); setPagina(1) }}
                className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
            </div>
          </>
        )}
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="ml-3 text-sm text-gray-600">Cargando seguimiento...</p>
        </div>
      )}

      {isError && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">
          Error al cargar los datos de seguimiento.
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="rounded-md bg-blue-50 p-4 text-sm text-blue-800">
          No se encontraron resultados de seguimiento con los filtros seleccionados.
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="overflow-x-auto rounded-md border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Nombre</th>
                <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Email</th>
                <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Comisión</th>
                <th className="px-3 py-2 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Progreso</th>
                <th className="px-3 py-2 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {data.items.map((alumno) => (
                <tr key={alumno.entrada_padron_id} className={alumno.estado === 'atrasado' ? 'bg-red-50' : 'bg-green-50'}>
                  <td className="whitespace-nowrap px-3 py-2 text-sm font-medium text-gray-900">
                    {alumno.nombre} {alumno.apellidos}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2 text-sm text-gray-600">{alumno.email}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-sm text-gray-600">{alumno.comision ?? '—'}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-center text-sm text-gray-900">
                    {alumno.aprobadas}/{alumno.total_actividades}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2 text-center">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${
                        alumno.estado === 'atrasado'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-green-100 text-green-800'
                      }`}
                    >
                      {alumno.estado === 'atrasado' ? 'Atrasado' : 'Al Día'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {totalPaginas > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3">
              <p className="text-sm text-gray-600">
                Página {data.pagina} de {totalPaginas} ({data.total} resultados)
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setPagina((p) => Math.max(1, p - 1))}
                  disabled={pagina <= 1}
                  className="rounded-md bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
                  disabled={pagina >= totalPaginas}
                  className="rounded-md bg-gray-100 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Siguiente
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
