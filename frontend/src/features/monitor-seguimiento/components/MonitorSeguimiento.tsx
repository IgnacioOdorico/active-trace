import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useMonitorSeguimiento } from '../hooks/useMonitoresApi'
import { Input } from '../../../shared/components/ui/Input'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

export default function MonitorSeguimiento() {
  const { user } = useAuth()
  const { data: materias } = useMaterias()
  const isCoordinador = user?.roles.includes('coordinador')

  const [materiaId, setMateriaId] = useState('')
  const [comision, setComision] = useState('')
  const [actividadMinima, setActividadMinima] = useState('')
  const [fechaDesde, setFechaDesde] = useState('')
  const [fechaHasta, setFechaHasta] = useState('')
  const [pagina, setPagina] = useState(1)

  const { data, isLoading, isError } = useMonitorSeguimiento({
    materia_id: isCoordinador ? (materiaId || undefined) : undefined,
    comision: comision || undefined,
    actividad_minima: actividadMinima || undefined,
    desde: isCoordinador ? (fechaDesde || undefined) : undefined,
    hasta: isCoordinador ? (fechaHasta || undefined) : undefined,
    pagina,
    por_pagina: 50,
  })

  const totalPaginas = data ? Math.ceil(data.total / data.por_pagina) : 0

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 rounded neo-latex-border bg-surface-container-lowest p-4">
        <div className="flex flex-col gap-1">
          <label htmlFor="seg-materia" className="font-label-caps text-label-caps text-on-surface-variant uppercase">Materia</label>
          <select
            id="seg-materia"
            value={materiaId}
            onChange={(e) => { setMateriaId(e.target.value); setPagina(1) }}
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
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
            <p className="mt-1 font-body-md text-[12px] text-on-surface-variant">Solo sus materias asignadas</p>
          )}
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="seg-comision" className="font-label-caps text-label-caps text-on-surface-variant uppercase">Comisión</label>
          <Input
            id="seg-comision"
            type="text"
            value={comision}
            onChange={(e) => { setComision(e.target.value); setPagina(1) }}
            placeholder="Ej: A"
            className="w-full"
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor="seg-actividad" className="font-label-caps text-label-caps text-on-surface-variant uppercase">
            Actividad mínima
          </label>
          <Input
            id="seg-actividad"
            type="text"
            value={actividadMinima}
            onChange={(e) => { setActividadMinima(e.target.value); setPagina(1) }}
            placeholder="Ej: TP1"
            className="w-full"
          />
        </div>

        {isCoordinador && (
          <>
            <div className="flex flex-col gap-1">
              <label htmlFor="seg-fecha-desde" className="font-label-caps text-label-caps text-on-surface-variant uppercase">Fecha desde</label>
              <Input
                id="seg-fecha-desde"
                type="date"
                value={fechaDesde}
                onChange={(e) => { setFechaDesde(e.target.value); setPagina(1) }}
                className="w-full"
              />
            </div>
            <div className="flex flex-col gap-1">
              <label htmlFor="seg-fecha-hasta" className="font-label-caps text-label-caps text-on-surface-variant uppercase">Fecha hasta</label>
              <Input
                id="seg-fecha-hasta"
                type="date"
                value={fechaHasta}
                onChange={(e) => { setFechaHasta(e.target.value); setPagina(1) }}
                className="w-full"
              />
            </div>
          </>
        )}
      </div>

      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="ml-3 font-body-md text-on-surface-variant">Cargando seguimiento...</p>
        </div>
      )}

      {isError && (
        <div className="rounded neo-latex-border bg-error-container p-4 font-body-md text-on-error-container">
          Error al cargar los datos de seguimiento.
        </div>
      )}

      {data && data.items.length === 0 && (
        <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
          No se encontraron resultados de seguimiento con los filtros seleccionados.
        </div>
      )}

      {data && data.items.length > 0 && (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Email</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Comisión</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Progreso</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {data.items.map((alumno) => (
                <tr key={alumno.entrada_padron_id} className="hover:bg-surface-container transition-colors">
                  <td className="whitespace-nowrap px-4 py-3 font-body-md text-body-md font-medium text-on-surface">
                    {alumno.nombre} {alumno.apellidos}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{alumno.email}</td>
                  <td className="whitespace-nowrap px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{alumno.comision ?? '—'}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-center font-mono-data text-mono-data text-on-surface">
                    {alumno.aprobadas}/{alumno.total_actividades}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-center">
                    <Badge
                      variant={alumno.estado === 'atrasado' ? 'error' : 'success'}
                    >
                      {alumno.estado === 'atrasado' ? 'Atrasado' : 'Al Día'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {totalPaginas > 1 && (
            <div className="flex items-center justify-between border-t border-outline-variant bg-surface px-4 py-3">
              <p className="font-body-md text-[12px] text-on-surface-variant">
                Página {data.pagina} de {totalPaginas} ({data.total} resultados)
              </p>
              <div className="flex gap-2">
                <Button
                  onClick={() => setPagina((p) => Math.max(1, p - 1))}
                  disabled={pagina <= 1}
                  variant="secondary"
                >
                  Anterior
                </Button>
                <Button
                  onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
                  disabled={pagina >= totalPaginas}
                  variant="secondary"
                >
                  Siguiente
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
