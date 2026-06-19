import { useState } from 'react'
import { useConvocatorias, useCerrarConvocatoria } from '../hooks/useColoquiosApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'
import type { Convocatoria } from '../types'
import { Button } from '../../../shared/components/ui/Button'

interface ListadoConvocatoriasProps {
  onEditar: (conv: Convocatoria) => void
  onImportar: (convId: string) => void
}

export default function ListadoConvocatorias({
  onEditar,
  onImportar,
}: ListadoConvocatoriasProps) {
  const { data, isLoading, isError } = useConvocatorias()
  const { data: materias } = useMaterias()
  const { data: cohortes } = useCohortes()
  const cerrar = useCerrarConvocatoria()
  const [cerrandoId, setCerrandoId] = useState<string | null>(null)

  if (isLoading) return <div className="py-8 text-center font-body-md text-on-surface-variant">Cargando convocatorias...</div>
  if (isError) return <div className="py-8 text-center font-body-md text-error">Error al cargar convocatorias.</div>

  const convocatorias = data?.items ?? []
  const nombreMateria = (id: string) => materias?.find((m) => m.id === id)?.nombre ?? id
  const nombreCohorte = (id: string) => cohortes?.find((c) => c.id === id)?.nombre ?? id

  if (convocatorias.length === 0) {
    return (
      <div className="rounded neo-latex-border bg-surface-container py-12 text-center font-body-md text-on-surface-variant">
        No hay convocatorias registradas.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
      <table className="min-w-full divide-y divide-outline-variant">
        <thead className="bg-surface">
          <tr>
            {[
              'Materia',
              'Cohorte',
              'Tipo',
              'Instancia',
              'Días generados',
              'Convocados',
              'Reservas',
              'Cupos libres',
              'Acciones',
            ].map((h) => (
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
          {convocatorias.map((conv) => (
            <tr key={conv.id} className="hover:bg-surface-container transition-colors">
              <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{nombreMateria(conv.materia_id)}</td>
              <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{nombreCohorte(conv.cohorte_id)}</td>
              <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{conv.tipo}</td>
              <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{conv.instancia}</td>
              <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface-variant">{conv.dias_disponibles}</td>
              <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface">{conv.total_convocados}</td>
              <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface">{conv.total_reservas_activas}</td>
              <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface">{conv.total_cupos_libres}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-2">
                  <Button
                    onClick={() => onEditar(conv)}
                    variant="ghost"
                    size="sm"
                  >
                    Editar
                  </Button>
                  <Button
                    onClick={() => onImportar(conv.id)}
                    variant="ghost"
                    size="sm"
                  >
                    Importar alumnos
                  </Button>
                  <Button
                    onClick={() => {
                      setCerrandoId(conv.id)
                      cerrar.mutate(conv.id, { onSettled: () => setCerrandoId(null) })
                    }}
                    disabled={cerrandoId === conv.id}
                    variant="ghost"
                    size="sm"
                    className="!text-error hover:!bg-error/10"
                  >
                    {cerrandoId === conv.id ? 'Cerrando...' : 'Cerrar'}
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
