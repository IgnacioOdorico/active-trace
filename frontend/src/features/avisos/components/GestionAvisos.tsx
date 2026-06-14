import { useState } from 'react'
import { useAvisosGestion, useEliminarAviso } from '../hooks/useAvisosApi'
import AvisoForm from './AvisoForm'
import type { Aviso } from '../types'

const SEVERIDAD_COLORS = {
  info: 'bg-blue-100 text-blue-700',
  warning: 'bg-yellow-100 text-yellow-700',
  error: 'bg-red-100 text-red-700',
}

export default function GestionAvisos() {
  const { data, isLoading, isError } = useAvisosGestion()
  const eliminar = useEliminarAviso()
  const [editando, setEditando] = useState<Aviso | null>(null)
  const [creando, setCreando] = useState(false)

  if (isLoading) return <div className="py-8 text-center text-gray-500">Cargando avisos...</div>
  if (isError) return <div className="py-8 text-center text-red-600">Error al cargar avisos.</div>

  const avisos = data?.data ?? []

  if (creando || editando) {
    return (
      <div>
        <h2 className="mb-4 text-lg font-semibold text-gray-800">
          {editando ? 'Editar aviso' : 'Nuevo aviso'}
        </h2>
        <AvisoForm
          aviso={editando ?? undefined}
          onSuccess={() => {
            setEditando(null)
            setCreando(false)
          }}
          onCancel={() => {
            setEditando(null)
            setCreando(false)
          }}
        />
      </div>
    )
  }

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <button
          type="button"
          onClick={() => setCreando(true)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          + Nuevo aviso
        </button>
      </div>

      {avisos.length === 0 ? (
        <div className="rounded-lg bg-gray-50 py-12 text-center text-gray-500">
          No hay avisos publicados.
        </div>
      ) : (
        <div className="space-y-3">
          {[...avisos]
            .sort((a, b) => a.orden - b.orden)
            .map((aviso) => (
              <div
                key={aviso.id}
                className="flex items-start justify-between rounded-lg border border-gray-200 bg-white p-4"
              >
                <div className="flex-1">
                  <div className="mb-1 flex items-center gap-2">
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${SEVERIDAD_COLORS[aviso.severidad]}`}
                    >
                      {aviso.severidad}
                    </span>
                    <span className="text-xs text-gray-500">{aviso.alcance}</span>
                    {aviso.requiere_ack && (
                      <span className="inline-flex rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-700">
                        req. ack
                      </span>
                    )}
                    <span className="text-xs text-gray-400">
                      acks: {aviso.total_acks}
                    </span>
                  </div>
                  <p className="font-medium text-gray-900">{aviso.titulo}</p>
                  <p className="mt-1 text-sm text-gray-600">{aviso.cuerpo}</p>
                  <p className="mt-1 text-xs text-gray-400">
                    {aviso.vigencia_inicio} → {aviso.vigencia_fin}
                  </p>
                </div>
                <div className="ml-4 flex gap-2">
                  <button
                    type="button"
                    onClick={() => setEditando(aviso)}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    Editar
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      if (confirm('¿Eliminar este aviso?')) eliminar.mutate(aviso.id)
                    }}
                    className="text-xs text-red-600 hover:underline"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  )
}
