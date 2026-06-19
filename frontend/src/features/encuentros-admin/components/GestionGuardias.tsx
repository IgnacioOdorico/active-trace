import { useMemo, useState } from 'react'
import { useGuardias, useExportarGuardias } from '../hooks/useEncuentrosAdminApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCarreras } from '../../estructura-academica/hooks/useEstructuraApi'
import type { GuardiasFilters, GuardiaEstado } from '../types'
import { Input } from '../../../shared/components/ui/Input'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

export default function GestionGuardias() {
  const [filters, setFilters] = useState<GuardiasFilters>({})
  const { data, isLoading, isError } = useGuardias(filters)
  const exportar = useExportarGuardias()
  const { data: materias } = useMaterias()
  const { data: carreras } = useCarreras()

  const nombreMateria = useMemo(() => {
    const mapa = new Map(materias?.map((m) => [m.id, m.nombre]))
    return (materiaId: string) => mapa.get(materiaId) ?? materiaId
  }, [materias])

  const nombreCarrera = useMemo(() => {
    const mapa = new Map(carreras?.map((c) => [c.id, c.nombre]))
    return (carreraId: string) => mapa.get(carreraId) ?? carreraId
  }, [carreras])

  const handleFilter = (key: keyof GuardiasFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }))
  }

  if (isLoading) return <div className="py-8 text-center font-body-md text-on-surface-variant">Cargando guardias...</div>
  if (isError) return <div className="py-8 text-center font-body-md text-error">Error al cargar guardias.</div>

  const guardias = data?.items ?? []

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <Input
          type="text"
          placeholder="Materia ID"
          onChange={(e) => handleFilter('materia_id', e.target.value)}
        />
        <Input
          type="text"
          placeholder="Asignación ID"
          onChange={(e) => handleFilter('asignacion_id', e.target.value)}
        />
        <div className="ml-auto">
          <Button
            onClick={() => exportar.mutate()}
            disabled={exportar.isPending}
            variant="secondary"
          >
            {exportar.isPending ? 'Exportando...' : 'Exportar'}
          </Button>
        </div>
      </div>

      {guardias.length === 0 ? (
        <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
          No hay guardias para los filtros seleccionados.
        </div>
      ) : (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                {['Materia', 'Carrera', 'Día', 'Horario', 'Estado', 'Comentarios'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {guardias.map((g) => (
                <tr key={g.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{nombreMateria(g.materia_id)}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{nombreCarrera(g.carrera_id)}</td>
                  <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface-variant">{g.dia}</td>
                  <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface-variant">{g.horario}</td>
                  <td className="px-4 py-3">
                    <Badge
                      variant={
                        g.estado === 'Realizada'
                          ? 'success'
                          : g.estado === 'Cancelada'
                          ? 'error'
                          : 'warning'
                      }
                    >
                      {g.estado}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{g.comentarios ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
