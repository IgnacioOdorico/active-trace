import { useState } from 'react'
import { useConvocatorias, useCerrarConvocatoria } from '../hooks/useColoquiosApi'
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
  const cerrar = useCerrarConvocatoria()
  const [cerrandoId, setCerrandoId] = useState<string | null>(null)

  if (isLoading) return <div className="py-8 text-center text-gray-500">Cargando convocatorias...</div>
  if (isError) return <div className="py-8 text-center text-red-600">Error al cargar convocatorias.</div>

  const convocatorias = data?.data ?? []

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
              'Instancia',
              'Días',
              'Cupo/día',
              'Convocados',
              'Reservas',
              'Cupos libres',
              'Estado',
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
              <td className="px-4 py-3 text-sm text-gray-900">{conv.materia_nombre}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{conv.instancia}</td>
              <td className="px-4 py-3 text-sm text-gray-600">
                {conv.dias_disponibles.join(', ')}
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">{conv.cupo_por_dia}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{conv.convocados}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{conv.reservas_activas}</td>
              <td className="px-4 py-3 text-sm text-gray-900">{conv.cupos_libres}</td>
              <td className="px-4 py-3">
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    conv.estado === 'activa'
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-600'
                  }`}
                >
                  {conv.estado}
                </span>
              </td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-2">
                  {conv.estado === 'activa' && (
                    <>
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
                    </>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
