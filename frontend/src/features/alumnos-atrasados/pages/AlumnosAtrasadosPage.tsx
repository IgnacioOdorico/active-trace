import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useAtrasadosApi } from '../hooks/useAtrasadosApi'
import type { Atrasado } from '../types'

function severityInfo(atrasado: Atrasado) {
  const ratio = atrasado.actividades_no_aprobadas / atrasado.total_actividades
  if (ratio > 0.5) {
    return {
      label: 'Crítico',
      badgeClass: 'bg-red-100 text-red-800',
      rowClass: 'border-red-300',
      bgClass: 'bg-red-50',
    }
  }
  if (ratio >= 0.25) {
    return {
      label: 'Atención',
      badgeClass: 'bg-yellow-100 text-yellow-800',
      rowClass: 'border-yellow-300',
      bgClass: 'bg-yellow-50',
    }
  }
  return {
    label: 'Seguimiento',
    badgeClass: 'bg-green-100 text-green-800',
    rowClass: 'border-green-300',
    bgClass: 'bg-green-50',
  }
}

export default function AlumnosAtrasadosPage() {
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const [materiaId, setMateriaId] = useState('')
  const [pagina, setPagina] = useState(1)
  const navigate = useNavigate()
  const { data, isLoading, isError } = useAtrasadosApi({
    materia_id: materiaId,
    pagina,
    por_pagina: 50,
  })

  const totalPaginas = data ? Math.ceil(data.total / data.por_pagina) : 0

  function handleComunicar(atrasado: Atrasado) {
    const params = new URLSearchParams()
    params.set('destinatario_email', atrasado.email)
    if (materiaId) params.set('materia_id', materiaId)
    navigate(`/comunicaciones?${params}`)
  }

  return (
    <div className="mx-auto max-w-6xl py-8">
      <h1 className="text-2xl font-bold text-gray-900">Alumnos Atrasados</h1>

      <div className="mt-6">
        <label htmlFor="materia" className="block text-sm font-medium text-gray-700">
          Materia
        </label>
        <select
          id="materia"
          value={materiaId}
          onChange={(e) => { setMateriaId(e.target.value); setPagina(1) }}
          className="mt-1 block w-full max-w-md rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="">Seleccione una materia</option>
          {materiasLoading && <option value="" disabled>Cargando materias...</option>}
          {materias?.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre}{m.comision ? ` - ${m.comision}` : ''}
            </option>
          ))}
        </select>
      </div>

      {!materiaId && (
        <p className="mt-8 text-center text-sm text-gray-500">
          Seleccione una materia para ver el ranking de alumnos atrasados.
        </p>
      )}

      {isLoading && materiaId && (
        <div className="mt-8 flex items-center justify-center py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="ml-3 text-sm text-gray-600">Cargando ranking...</p>
        </div>
      )}

      {isError && materiaId && (
        <div className="mt-8 rounded-md bg-red-50 p-4 text-sm text-red-800">
          Error al cargar los datos. Intente nuevamente.
        </div>
      )}

      {data && data.data.length === 0 && (
        <div className="mt-8 rounded-md bg-blue-50 p-4 text-sm text-blue-800">
          No se encontraron alumnos atrasados para esta materia.
        </div>
      )}

      {data && data.data.length > 0 && (
        <div className="mt-6 overflow-x-auto rounded-md border border-gray-200">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Nombre</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Comisión</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">No Aprobadas</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Total</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Progreso</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Gravedad</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Última Actividad</th>
                <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {data.data.map((a) => {
                const sev = severityInfo(a)
                return (
                  <tr key={a.id} className={`${sev.bgClass} border-l-4 ${sev.rowClass}`}>
                    <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">
                      {a.nombre} {a.apellidos}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{a.comision}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-center text-sm font-semibold text-gray-900">
                      {a.actividades_no_aprobadas}
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-center text-sm text-gray-600">{a.total_actividades}</td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-24 overflow-hidden rounded-full bg-gray-200">
                          <div
                            className="h-full rounded-full bg-blue-600"
                            style={{ width: `${a.progreso}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-500">{a.progreso}%</span>
                      </div>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${sev.badgeClass}`}>
                        {sev.label}
                      </span>
                    </td>
                    <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{a.ultima_actividad}</td>
                    <td className="whitespace-nowrap px-4 py-3 text-center">
                      <button
                        onClick={() => handleComunicar(a)}
                        className="rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700"
                      >
                        Comunicar
                      </button>
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
