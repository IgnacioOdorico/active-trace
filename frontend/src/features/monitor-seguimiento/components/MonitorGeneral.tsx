import { useState } from 'react'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useMonitorGeneral } from '../hooks/useMonitoresApi'

export default function MonitorGeneral() {
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const [materiaId, setMateriaId] = useState('')
  const [comision, setComision] = useState('')
  const [regional, setRegional] = useState('')
  const [busqueda, setBusqueda] = useState('')
  const [estado, setEstado] = useState('')
  const [pagina, setPagina] = useState(1)

  const { data, isLoading, isError } = useMonitorGeneral({
    materia_id: materiaId || undefined,
    comision: comision || undefined,
    regional: regional || undefined,
    q: busqueda || undefined,
    estado: estado || undefined,
    pagina,
    por_pagina: 50,
  })

  const totalPaginas = data ? Math.ceil(data.total / data.por_pagina) : 0

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <div>
          <label htmlFor="mon-materia" className="block text-xs font-medium text-gray-700">Materia</label>
          <select
            id="mon-materia"
            value={materiaId}
            onChange={(e) => { setMateriaId(e.target.value); setPagina(1) }}
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Todas</option>
            {materiasLoading && <option value="" disabled>Cargando...</option>}
            {materias?.map((m) => (
              <option key={m.id} value={m.id}>{m.nombre}</option>
            ))}
          </select>
        </div>

        <div>
          <label htmlFor="mon-comision" className="block text-xs font-medium text-gray-700">Comisión</label>
          <input
            id="mon-comision"
            type="text"
            value={comision}
            onChange={(e) => { setComision(e.target.value); setPagina(1) }}
            placeholder="Ej: A"
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="mon-regional" className="block text-xs font-medium text-gray-700">Regional</label>
          <input
            id="mon-regional"
            type="text"
            value={regional}
            onChange={(e) => { setRegional(e.target.value); setPagina(1) }}
            placeholder="Ej: Centro"
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="mon-busqueda" className="block text-xs font-medium text-gray-700">Búsqueda</label>
          <input
            id="mon-busqueda"
            type="text"
            value={busqueda}
            onChange={(e) => { setBusqueda(e.target.value); setPagina(1) }}
            placeholder="Nombre del alumno"
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div>
          <label htmlFor="mon-estado" className="block text-xs font-medium text-gray-700">Estado</label>
          <select
            id="mon-estado"
            value={estado}
            onChange={(e) => { setEstado(e.target.value); setPagina(1) }}
            className="mt-1 block w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">Todos</option>
            <option value="atrasado">Atrasado</option>
            <option value="al_dia">Al Día</option>
          </select>
        </div>
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="ml-3 text-sm text-gray-600">Cargando monitores...</p>
        </div>
      )}

      {isError && (
        <div className="rounded-md bg-red-50 p-4 text-sm text-red-800">
          Error al cargar los datos del monitor.
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="rounded-md bg-blue-50 p-4 text-sm text-blue-800">
          No se encontraron resultados con los filtros seleccionados.
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
                <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Regional</th>
                <th className="px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Materia</th>
                <th className="px-3 py-2 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Total</th>
                <th className="px-3 py-2 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Aprobadas</th>
                <th className="px-3 py-2 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {data.items.map((alumno) => {
                const materiaNombre = alumno.materia_id
                  ? (materias?.find((m) => m.id === alumno.materia_id)?.nombre ?? alumno.materia_id)
                  : '—'
                return (
                <tr
                  key={alumno.entrada_padron_id}
                  className={alumno.estado === 'atrasado' ? 'bg-red-50' : 'bg-green-50'}
                >
                  <td className="whitespace-nowrap px-3 py-2 text-sm font-medium text-gray-900">
                    {alumno.nombre} {alumno.apellidos}
                  </td>
                  <td className="whitespace-nowrap px-3 py-2 text-sm text-gray-600">{alumno.email}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-sm text-gray-600">{alumno.comision ?? '—'}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-sm text-gray-600">{alumno.regional ?? '—'}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-sm text-gray-600">{materiaNombre}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-center text-sm text-gray-900">{alumno.total_actividades}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-center text-sm text-gray-900">{alumno.aprobadas}</td>
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
                )
              })}
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
