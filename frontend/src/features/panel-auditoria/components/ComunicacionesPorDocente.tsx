import { useComunicacionesPorDocente } from '../hooks/usePanelAuditoriaApi'
import type { PanelFilters } from '../types'

interface Props {
  filters: PanelFilters
}

const ESTADOS = ['pendiente', 'enviando', 'enviado', 'fallido', 'cancelado'] as const
const COLORES: Record<string, string> = {
  pendiente: 'bg-yellow-100 text-yellow-700',
  enviando: 'bg-blue-100 text-blue-700',
  enviado: 'bg-green-100 text-green-700',
  fallido: 'bg-red-100 text-red-700',
  cancelado: 'bg-gray-100 text-gray-600',
}

export default function ComunicacionesPorDocente({ filters }: Props) {
  const { data, isLoading } = useComunicacionesPorDocente(filters)

  if (isLoading) {
    return <div className="h-32 animate-pulse rounded-lg bg-gray-200" />
  }

  if (!data || data.length === 0) {
    return (
      <p className="py-6 text-center text-sm text-gray-500">
        Sin datos de comunicaciones para el rango seleccionado.
      </p>
    )
  }

  return (
    <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
      <thead className="bg-gray-50">
        <tr>
          <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Docente</th>
          {ESTADOS.map((e) => (
            <th key={e} className="px-4 py-2 text-center text-xs font-medium capitalize text-gray-500">
              {e}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr key={item.docente_id} className="border-b border-gray-100 hover:bg-gray-50">
            <td className="px-4 py-2 text-sm font-medium text-gray-900">{item.docente_nombre}</td>
            {ESTADOS.map((estado) => (
              <td key={estado} className="px-4 py-2 text-center">
                {item[estado] > 0 && (
                  <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${COLORES[estado]}`}>
                    {item[estado]}
                  </span>
                )}
                {item[estado] === 0 && (
                  <span className="text-xs text-gray-300">—</span>
                )}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
