import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useReportesApi } from '../hooks/useReportesApi'
import type { NotaFinalAlumno } from '../types'

function downloadCsv(alumnos: NotaFinalAlumno[], filename: string) {
  const headers = ['Nombre', 'Apellidos', 'Comisión', 'Nota Final', 'Actividades Textuales', 'Estado']
  const rows = alumnos.map((a) => [
    a.nombre,
    a.apellidos,
    a.comision,
    String(a.nota_final),
    a.actividades_textuales.join('; '),
    a.estado === 'aprobado' ? 'Aprobado' : 'No Aprobado',
  ])
  const csvContent = [
    headers.join(','),
    ...rows.map((r) => r.map((c) => `"${c.replace(/"/g, '""')}"`).join(',')),
  ].join('\n')

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export default function ReportesPage() {
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const [materiaId, setMateriaId] = useState('')
  const [selectedActividadIds, setSelectedActividadIds] = useState<string[]>([])
  const [showTooltipId, setShowTooltipId] = useState<string | null>(null)
  const navigate = useNavigate()

  const { metrics, actividades, calcularNotaFinal } = useReportesApi(materiaId || null)

  const [resultados, setResultados] = useState<NotaFinalAlumno[] | null>(null)

  function handleCalcular() {
    if (!materiaId || selectedActividadIds.length === 0) return
    calcularNotaFinal.mutate(
      { materia_id: materiaId, actividades: selectedActividadIds },
      {
        onSuccess: (data) => {
          setResultados(data)
        },
      },
    )
  }

  function handleMateriaChange(value: string) {
    setMateriaId(value)
    setSelectedActividadIds([])
    setResultados(null)
  }

  function toggleActividad(id: string) {
    setSelectedActividadIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    )
  }

  const met = metrics.data
  const showEmpty = met?.sin_datos

  return (
    <div className="mx-auto max-w-6xl py-8">
      <h1 className="text-2xl font-bold text-gray-900">Reportes y Notas Finales</h1>

      <div className="mt-6">
        <label htmlFor="materia" className="block text-sm font-medium text-gray-700">
          Materia
        </label>
        <select
          id="materia"
          value={materiaId}
          onChange={(e) => handleMateriaChange(e.target.value)}
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
          Seleccione una materia para ver reportes y notas finales.
        </p>
      )}

      {metrics.isLoading && materiaId && (
        <div className="mt-8 flex items-center justify-center py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="ml-3 text-sm text-gray-600">Cargando métricas...</p>
        </div>
      )}

      {metrics.isError && materiaId && (
        <div className="mt-8 rounded-md bg-red-50 p-4 text-sm text-red-800">
          Error al cargar las métricas. Intente nuevamente.
        </div>
      )}

      {showEmpty && (
        <div className="mt-8 rounded-md bg-yellow-50 p-6 text-center">
          <p className="text-sm font-medium text-yellow-800">
            No hay datos de calificaciones para esta materia.
          </p>
          <button
            onClick={() => navigate('/calificaciones/importar')}
            className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            Ir a Importar Calificaciones
          </button>
        </div>
      )}

      {met && !showEmpty && (
        <>
          <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-sm font-medium text-gray-500">Total Alumnos</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{met.total_alumnos}</p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-sm font-medium text-gray-500">Total Actividades</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{met.total_actividades}</p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-sm font-medium text-gray-500">Total Calificaciones</p>
              <p className="mt-1 text-2xl font-bold text-gray-900">{met.total_calificaciones}</p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-sm font-medium text-gray-500">Promedio Aprobación</p>
              <p className={`mt-1 text-2xl font-bold ${met.promedio_aprobacion_general >= 60 ? 'text-green-600' : 'text-red-600'}`}>
                {met.promedio_aprobacion_general}%
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-sm font-medium text-gray-500">Alumnos Aprobados</p>
              <p className="mt-1 text-2xl font-bold text-green-600">{met.alumnos_aprobados_count}</p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-4">
              <p className="text-sm font-medium text-gray-500">Alumnos Atrasados</p>
              <p className="mt-1 text-2xl font-bold text-red-600">{met.alumnos_atrasados_count}</p>
            </div>
          </div>

          <div className="mt-10">
            <h2 className="text-lg font-semibold text-gray-900">Calcular Nota Final</h2>
            <p className="mt-1 text-sm text-gray-500">
              Seleccione las actividades numéricas a incluir en el promedio.
            </p>

            {actividades.isLoading && (
              <div className="mt-4 flex items-center gap-2 text-sm text-gray-600">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
                Cargando actividades...
              </div>
            )}

            {actividades.data && (
              <div className="mt-4 flex flex-wrap gap-2">
                {actividades.data.map((act) => {
                  const isTextual = act.tipo === 'textual'
                  const selected = selectedActividadIds.includes(act.id)
                  return (
                    <button
                      key={act.id}
                      type="button"
                      disabled={isTextual}
                      onClick={() => !isTextual && toggleActividad(act.id)}
                      className={`inline-flex items-center gap-1.5 rounded-md border px-3 py-1.5 text-sm font-medium transition-colors ${
                        isTextual
                          ? 'cursor-not-allowed border-gray-200 bg-gray-50 text-gray-400'
                          : selected
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-300 bg-white text-gray-700 hover:bg-gray-50'
                      }`}
                      onMouseEnter={() => isTextual && setShowTooltipId(act.id)}
                      onMouseLeave={() => setShowTooltipId(null)}
                    >
                      {act.nombre}
                      {isTextual && (
                        <span className="relative inline-flex items-center rounded bg-gray-200 px-1.5 py-0.5 text-xs font-semibold text-gray-600">
                          Textual
                          {showTooltipId === act.id && (
                            <span className="absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded bg-gray-800 px-2 py-1 text-xs text-white">
                              Las actividades textuales no se incluyen en el promedio numérico
                            </span>
                          )}
                        </span>
                      )}
                    </button>
                  )
                })}
              </div>
            )}

            <button
              onClick={handleCalcular}
              disabled={selectedActividadIds.length === 0 || calcularNotaFinal.isPending}
              className="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {calcularNotaFinal.isPending ? 'Calculando...' : 'Calcular Nota Final'}
            </button>

            {calcularNotaFinal.isError && (
              <div className="mt-4 rounded-md bg-red-50 p-3 text-sm text-red-800">
                {calcularNotaFinal.error instanceof Error
                  ? calcularNotaFinal.error.message
                  : 'Error al calcular nota final'}
              </div>
            )}
          </div>

          {resultados && resultados.length > 0 && (
            <div className="mt-8">
              <div className="mb-4 flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">Resultados</h3>
                <button
                  onClick={() => downloadCsv(resultados, `notas-finales-${materiaId}.csv`)}
                  className="rounded-md bg-green-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-green-700"
                >
                  Descargar CSV
                </button>
              </div>

              <div className="overflow-x-auto rounded-md border border-gray-200">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Nombre</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Apellidos</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Comisión</th>
                      <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Nota Final</th>
                      <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Act. Textuales</th>
                      <th className="px-4 py-3 text-center text-xs font-medium uppercase tracking-wider text-gray-500">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 bg-white">
                    {resultados.map((alumno, idx) => (
                      <tr key={idx} className={alumno.estado === 'aprobado' ? '' : 'bg-red-50'}>
                        <td className="whitespace-nowrap px-4 py-3 text-sm font-medium text-gray-900">{alumno.nombre}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{alumno.apellidos}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-600">{alumno.comision}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-center text-sm font-semibold text-gray-900">
                          {alumno.nota_final.toFixed(1)}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-sm text-gray-600">
                          {alumno.actividades_textuales.length > 0
                            ? alumno.actividades_textuales.join(', ')
                            : '-'}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-center">
                          <span
                            className={`inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ${
                              alumno.estado === 'aprobado'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}
                          >
                            {alumno.estado === 'aprobado' ? 'Aprobado' : 'No Aprobado'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {resultados && resultados.length === 0 && (
            <div className="mt-8 rounded-md bg-blue-50 p-4 text-sm text-blue-800">
              No se encontraron resultados para las actividades seleccionadas.
            </div>
          )}
        </>
      )}
    </div>
  )
}
