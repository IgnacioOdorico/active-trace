import { useAvisosUsuario, useAckAviso } from '../hooks/useAvisosApi'

const SEVERIDAD_COLORS = {
  info: 'border-blue-300 bg-blue-50',
  warning: 'border-yellow-300 bg-yellow-50',
  error: 'border-red-300 bg-red-50',
}

export default function AvisosUsuario() {
  const { data, isLoading } = useAvisosUsuario()
  const ack = useAckAviso()

  if (isLoading) return <div className="py-4 text-sm text-gray-500">Cargando avisos...</div>

  const avisos = data?.data ?? []

  if (avisos.length === 0) return null

  return (
    <div className="mb-6 space-y-3">
      {avisos.map((aviso) => (
        <div
          key={aviso.id}
          className={`rounded-lg border-l-4 p-4 ${SEVERIDAD_COLORS[aviso.severidad]}`}
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="font-semibold text-gray-900">{aviso.titulo}</p>
              <p className="mt-1 text-sm text-gray-700">{aviso.cuerpo}</p>
            </div>
            {aviso.requiere_ack && (
              <button
                type="button"
                onClick={() => ack.mutate(aviso.id)}
                disabled={ack.isPending}
                className="ml-4 flex-shrink-0 rounded-md bg-white px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm ring-1 ring-gray-300 hover:bg-gray-50 disabled:opacity-50"
              >
                Confirmar lectura
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
