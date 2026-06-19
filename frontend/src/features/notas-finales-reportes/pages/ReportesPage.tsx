import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useReportesApi } from '../hooks/useReportesApi'
import type { NotaFinalAlumno } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

function downloadCsv(alumnos: NotaFinalAlumno[], filename: string) {
  const headers = ['Nombre', 'Apellidos', 'Comisión', 'Nota Final', 'Actividades Textuales', 'Estado']
  const rows = alumnos.map((a) => [
    a.nombre,
    a.apellidos,
    a.comision,
    a.nota_final !== null ? String(a.nota_final) : 'Sin nota',
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
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Reportes y Notas Finales</h1>
      </div>

      <BentoCard>
        <div className="flex flex-col gap-1 mb-6">
          <label htmlFor="materia" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Materia
          </label>
          <select
            id="materia"
            value={materiaId}
            onChange={(e) => handleMateriaChange(e.target.value)}
            className="w-full max-w-md neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
          <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
            Seleccione una materia para ver reportes y notas finales.
          </div>
        )}

        {metrics.isLoading && materiaId && (
          <div className="mt-8 flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <p className="ml-3 font-body-md text-on-surface-variant">Cargando métricas...</p>
          </div>
        )}

        {metrics.isError && materiaId && (
          <div className="mt-8 rounded neo-latex-border bg-error-container p-4 font-body-md text-on-error-container">
            Error al cargar las métricas. Intente nuevamente.
          </div>
        )}

        {showEmpty && (
          <div className="mt-8 rounded neo-latex-border bg-surface-container p-6 text-center">
            <p className="font-body-md font-medium text-on-surface-variant">
              No hay datos de calificaciones para esta materia.
            </p>
            <Button
              onClick={() => navigate('/calificaciones/importar')}
              variant="primary"
              className="mt-4"
            >
              Ir a Importar Calificaciones
            </Button>
          </div>
        )}

        {met && !showEmpty && (
          <>
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              <div className="rounded neo-latex-border bg-surface-container-lowest p-4">
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase">Total Alumnos</p>
                <p className="mt-1 font-mono-data text-[24px] font-bold text-on-surface">{met.total_alumnos}</p>
              </div>
              <div className="rounded neo-latex-border bg-surface-container-lowest p-4">
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase">Total Actividades</p>
                <p className="mt-1 font-mono-data text-[24px] font-bold text-on-surface">{met.total_actividades}</p>
              </div>
              <div className="rounded neo-latex-border bg-surface-container-lowest p-4">
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase">Total Calificaciones</p>
                <p className="mt-1 font-mono-data text-[24px] font-bold text-on-surface">{met.total_calificaciones}</p>
              </div>
              <div className="rounded neo-latex-border bg-surface-container-lowest p-4">
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase">Promedio Aprobación</p>
                <p className={`mt-1 font-mono-data text-[24px] font-bold ${met.promedio_aprobacion_general >= 60 ? 'text-success' : 'text-error'}`}>
                  {met.promedio_aprobacion_general}%
                </p>
              </div>
              <div className="rounded neo-latex-border bg-surface-container-lowest p-4">
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase">Alumnos Aprobados</p>
                <p className="mt-1 font-mono-data text-[24px] font-bold text-success">{met.alumnos_aprobados_count}</p>
              </div>
              <div className="rounded neo-latex-border bg-surface-container-lowest p-4">
                <p className="font-label-caps text-label-caps text-on-surface-variant uppercase">Alumnos Atrasados</p>
                <p className="mt-1 font-mono-data text-[24px] font-bold text-error">{met.alumnos_atrasados_count}</p>
              </div>
            </div>

            <div className="mt-10">
              <h2 className="font-headline-sm text-headline-sm text-on-surface">Calcular Nota Final</h2>
              <p className="mt-1 font-body-md text-on-surface-variant">
                Seleccione las actividades numéricas a incluir en el promedio.
              </p>

              {actividades.isLoading && (
                <div className="mt-4 flex items-center gap-2 font-body-md text-on-surface-variant">
                  <div className="h-4 w-4 animate-spin rounded-full border-2 border-primary border-t-transparent" />
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
                        className={`inline-flex items-center gap-1.5 rounded neo-latex-border px-3 py-1.5 font-body-md transition-colors ${
                          isTextual
                            ? 'cursor-not-allowed border-outline-variant bg-surface-container text-outline'
                            : selected
                              ? 'border-primary bg-primary/10 text-primary font-medium'
                              : 'bg-surface-container-lowest text-on-surface hover:bg-surface-container'
                        }`}
                        onMouseEnter={() => isTextual && setShowTooltipId(act.id)}
                        onMouseLeave={() => setShowTooltipId(null)}
                      >
                        {act.nombre}
                        {isTextual && (
                          <span className="relative inline-flex items-center">
                            <Badge variant="neutral">Textual</Badge>
                            {showTooltipId === act.id && (
                              <span className="absolute bottom-full left-1/2 z-10 mb-2 -translate-x-1/2 whitespace-nowrap rounded bg-[#002045] px-2 py-1 font-body-md text-[12px] text-white">
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

              <Button
                onClick={handleCalcular}
                disabled={selectedActividadIds.length === 0 || calcularNotaFinal.isPending}
                variant="primary"
                className="mt-6"
              >
                {calcularNotaFinal.isPending ? 'Calculando...' : 'Calcular Nota Final'}
              </Button>

              {calcularNotaFinal.isError && (
                <div className="mt-4 rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">
                  {calcularNotaFinal.error instanceof Error
                    ? calcularNotaFinal.error.message
                    : 'Error al calcular nota final'}
                </div>
              )}
            </div>

            {resultados && resultados.length > 0 && (
              <div className="mt-8 border-t border-outline-variant pt-8">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="font-headline-sm text-headline-sm text-on-surface">Resultados</h3>
                  <Button
                    onClick={() => downloadCsv(resultados, `notas-finales-${materiaId}.csv`)}
                    variant="primary"
                  >
                    <span className="material-symbols-outlined mr-1 text-[18px]">download</span>
                    Descargar CSV
                  </Button>
                </div>

                <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
                  <table className="min-w-full divide-y divide-outline-variant">
                    <thead className="bg-surface">
                      <tr>
                        <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Nombre</th>
                        <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Apellidos</th>
                        <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Comisión</th>
                        <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Nota Final</th>
                        <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Act. Textuales</th>
                        <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
                      {resultados.map((alumno, idx) => (
                        <tr key={idx} className={`hover:bg-surface-container transition-colors ${alumno.estado === 'aprobado' ? '' : 'bg-error-container/10'}`}>
                          <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{alumno.nombre}</td>
                          <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md text-on-surface-variant">{alumno.apellidos}</td>
                          <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md text-on-surface-variant">{alumno.comision}</td>
                          <td className="whitespace-nowrap px-4 py-3 text-center font-mono-data text-mono-data font-medium text-on-surface">
                            {alumno.nota_final !== null ? alumno.nota_final.toFixed(1) : '—'}
                          </td>
                          <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md text-on-surface-variant">
                            {alumno.actividades_textuales.length > 0
                              ? alumno.actividades_textuales.join(', ')
                              : '-'}
                          </td>
                          <td className="whitespace-nowrap px-4 py-3 text-center">
                            <Badge variant={alumno.estado === 'aprobado' ? 'success' : 'error'}>
                              {alumno.estado === 'aprobado' ? 'Aprobado' : 'No Aprobado'}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {resultados && resultados.length === 0 && (
              <div className="mt-8 rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
                No se encontraron resultados para las actividades seleccionadas.
              </div>
            )}
          </>
        )}
      </BentoCard>
    </div>
  )
}
