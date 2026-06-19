import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useAtrasadosApi } from '../hooks/useAtrasadosApi'
import type { Atrasado } from '../types'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

function severityInfo(atrasado: Atrasado) {
  const ratio = atrasado.actividades_no_aprobadas / atrasado.total_actividades
  if (ratio > 0.5) {
    return {
      label: 'Crítico',
      variant: 'error' as const,
      rowClass: 'border-l-4 border-error bg-error-container/20',
    }
  }
  if (ratio >= 0.25) {
    return {
      label: 'Atención',
      variant: 'warning' as const,
      rowClass: 'border-l-4 border-[#F2C94C] bg-[#F2C94C]/10',
    }
  }
  return {
    label: 'Seguimiento',
    variant: 'success' as const,
    rowClass: 'border-l-4 border-success bg-success/10',
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
    <div className="mx-auto max-w-6xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Alumnos Atrasados</h1>
      </div>

      <BentoCard>
        <div className="flex flex-col gap-1 mb-6">
          <label htmlFor="materia" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Materia
          </label>
          <select
            id="materia"
            value={materiaId}
            onChange={(e) => { setMateriaId(e.target.value); setPagina(1) }}
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
            Seleccione una materia para ver el ranking de alumnos atrasados.
          </div>
        )}

        {isLoading && materiaId && (
          <div className="mt-8 flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <p className="ml-3 font-body-md text-on-surface-variant">Cargando ranking...</p>
          </div>
        )}

        {isError && materiaId && (
          <div className="mt-8 rounded neo-latex-border bg-error-container p-4 font-body-md text-on-error-container">
            Error al cargar los datos. Intente nuevamente.
          </div>
        )}

        {data && data.data.length === 0 && (
          <div className="mt-8 rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
            No se encontraron alumnos atrasados para esta materia.
          </div>
        )}

        {data && data.data.length > 0 && (
          <>
            <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
              <table className="min-w-full divide-y divide-outline-variant">
                <thead className="bg-surface">
                  <tr>
                    <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Nombre</th>
                    <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Comisión</th>
                    <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">No Aprobadas</th>
                    <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Total</th>
                    <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Progreso</th>
                    <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Gravedad</th>
                    <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Última Actividad</th>
                    <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Acción</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
                  {data.data.map((a) => {
                    const sev = severityInfo(a)
                    return (
                      <tr key={a.id} className={`hover:bg-surface-container transition-colors ${sev.rowClass}`}>
                        <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md font-medium text-on-surface">
                          {a.nombre} {a.apellidos}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md text-on-surface-variant">{a.comision}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-center font-mono-data text-mono-data font-medium text-on-surface">
                          {a.actividades_no_aprobadas}
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 text-center font-mono-data text-mono-data text-on-surface-variant">{a.total_actividades}</td>
                        <td className="whitespace-nowrap px-4 py-3">
                          <div className="flex items-center gap-2">
                            <div className="h-2 w-24 overflow-hidden rounded-full bg-surface-container-high border border-outline-variant">
                              <div
                                className="h-full bg-primary"
                                style={{ width: `${a.progreso}%` }}
                              />
                            </div>
                            <span className="font-mono-data text-mono-data text-on-surface-variant">{a.progreso}%</span>
                          </div>
                        </td>
                        <td className="whitespace-nowrap px-4 py-3">
                          <Badge variant={sev.variant}>
                            {sev.label}
                          </Badge>
                        </td>
                        <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md text-on-surface-variant">{a.ultima_actividad}</td>
                        <td className="whitespace-nowrap px-4 py-3 text-center">
                          <Button
                            onClick={() => handleComunicar(a)}
                            variant="primary"
                            size="sm"
                          >
                            Comunicar
                          </Button>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>

            {totalPaginas > 1 && (
              <div className="flex items-center justify-between pt-4 font-body-md text-on-surface-variant border-t border-outline-variant mt-4">
                <p>
                  Página {data.pagina} de {totalPaginas} ({data.total} resultados)
                </p>
                <div className="flex gap-2">
                  <Button
                    onClick={() => setPagina((p) => Math.max(1, p - 1))}
                    disabled={pagina <= 1}
                    variant="secondary"
                    size="sm"
                  >
                    Anterior
                  </Button>
                  <Button
                    onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
                    disabled={pagina >= totalPaginas}
                    variant="secondary"
                    size="sm"
                  >
                    Siguiente
                  </Button>
                </div>
              </div>
            )}
          </>
        )}
      </BentoCard>
    </div>
  )
}
