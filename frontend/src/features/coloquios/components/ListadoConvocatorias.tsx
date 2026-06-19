import { useState } from 'react'
import { useConvocatorias, useCerrarConvocatoria } from '../hooks/useColoquiosApi'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useCohortes } from '../../estructura-academica/hooks/useEstructuraApi'
import type { Convocatoria } from '../types'

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

  if (isLoading) return <div className="py-8 text-center text-gray-500">Cargando convocatorias...</div>
  if (isError) return <div className="py-8 text-center text-red-600">Error al cargar convocatorias.</div>

  const convocatorias = data?.items ?? []
  const nombreMateria = (id: string) => materias?.find((m) => m.id === id)?.nombre ?? id
  const nombreCohorte = (id: string) => cohortes?.find((c) => c.id === id)?.nombre ?? id

  if (convocatorias.length === 0) {
    return (
      <div className="rounded-lg bg-gray-50 py-12 text-center text-gray-500">
        No hay convocatorias registradas.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
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
                className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-500"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100 bg-white">
          {convocatorias.map((conv) => (
            <tr key={conv.id} className="hover:bg-gray-50">
              <td className="px-4 py-3 text-sm text-gray-900">{nombreMateria(conv.materia_id)}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{nombreCohorte(conv.cohorte_id)}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{conv.tipo}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{conv.instancia}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{conv.dias_disponibles}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{conv.total_convocados}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{conv.total_reservas_activas}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{conv.total_cupos_libres}</td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={() => onEditar(conv)}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => onImportar(conv.id)}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Importar alumnos
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setCerrandoId(conv.id)
                      cerrar.mutate(conv.id, { onSettled: () => setCerrandoId(null) })
                    }}
                    disabled={cerrandoId === conv.id}
                    className="text-xs text-red-600 hover:underline disabled:opacity-50"
                  >
                    {cerrandoId === conv.id ? 'Cerrando...' : 'Cerrar'}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
