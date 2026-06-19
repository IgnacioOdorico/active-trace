import { useMemo, useState } from 'react'
import { useEncuentrosInstancias } from '../hooks/useEncuentrosAdminApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import type { EncuentrosFilters, EncuentroEstado } from '../types'
import { Input } from '../../../shared/components/ui/Input'
import { Badge } from '../../../shared/components/ui/Badge'

export default function EncuentrosTransversal() {
  const [filters, setFilters] = useState<EncuentrosFilters>({})
  const { data, isLoading, isError } = useEncuentrosInstancias(filters)
  const { data: materias } = useMaterias()

  const nombreMateria = useMemo(() => {
    const mapa = new Map(materias?.map((m) => [m.id, m.nombre]))
    return (materiaId: string) => mapa.get(materiaId) ?? materiaId
  }, [materias])

  const handleFilter = (key: keyof EncuentrosFilters, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }))
  }

  if (isLoading) return <div className="py-8 text-center font-body-md text-on-surface-variant">Cargando encuentros...</div>
  if (isError) return <div className="py-8 text-center font-body-md text-error">Error al cargar encuentros.</div>

  const encuentros = data?.items ?? []

  return (
    <div>
      <div className="mb-4 flex gap-3">
        <Input
          type="text"
          placeholder="Materia ID"
          onChange={(e) => handleFilter('materia_id', e.target.value)}
        />
        <select
          className="neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          onChange={(e) => handleFilter('estado', e.target.value)}
        >
          <option value="">Todos los estados</option>
          <option value="Programado">Programado</option>
          <option value="Realizado">Realizado</option>
          <option value="Cancelado">Cancelado</option>
        </select>
      </div>

      {encuentros.length === 0 ? (
        <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
          No hay encuentros para los filtros seleccionados.
        </div>
      ) : (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                {['Materia', 'Título', 'Fecha', 'Hora', 'Estado', 'Links'].map((h) => (
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
              {encuentros.map((enc) => (
                <tr key={enc.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{nombreMateria(enc.materia_id)}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{enc.titulo}</td>
                  <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface-variant">{enc.fecha}</td>
                  <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface-variant">{enc.hora}</td>
                  <td className="px-4 py-3">
                    <Badge
                      variant={
                        enc.estado === 'Realizado'
                          ? 'success'
                          : enc.estado === 'Cancelado'
                          ? 'error'
                          : 'warning'
                      }
                    >
                      {enc.estado}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 font-body-md text-body-md">
                    {enc.meet_url && (
                      <a
                        href={enc.meet_url}
                        target="_blank"
                        rel="noreferrer"
                        className="mr-2 text-primary hover:underline"
                      >
                        Meet
                      </a>
                    )}
                    {enc.video_url && (
                      <a
                        href={enc.video_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary hover:underline"
                      >
                        Grabación
                      </a>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
