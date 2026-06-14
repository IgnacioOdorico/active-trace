import { useState } from 'react'
import { useCerrarLiquidacion } from '../hooks/useLiquidacionesApi'
import type { Liquidacion } from '../types'

interface Props {
  liquidacion: Liquidacion
  onClosed: () => void
  onCancel: () => void
}

export default function CierreConfirmacion({ liquidacion, onClosed, onCancel }: Props) {
  const { mutate, isPending } = useCerrarLiquidacion()
  const [error, setError] = useState<string | null>(null)

  function handleConfirmar() {
    setError(null)
    mutate(liquidacion.id, {
      onSuccess: () => onClosed(),
      onError: (err: unknown) => {
        const status = (err as { response?: { status?: number } })?.response?.status
        if (status === 409) {
          setError('Esta liquidación ya estaba cerrada. El estado fue actualizado.')
          onClosed()
        } else {
          setError('Ocurrió un error al cerrar la liquidación. Intente nuevamente.')
        }
      },
    })
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <h2 className="mb-2 text-lg font-semibold text-gray-900">Cerrar liquidación</h2>
        <p className="mb-1 text-sm text-gray-600">
          Vas a cerrar la liquidación de{' '}
          <strong>{liquidacion.docente_nombre}</strong> para el período{' '}
          <strong>{liquidacion.periodo}</strong>.
        </p>
        <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm font-medium text-red-700">
          Esta acción es irreversible. Una vez cerrada, la liquidación no puede reabrirse.
        </p>

        {error && (
          <p className="mb-3 rounded-lg bg-yellow-50 p-3 text-sm text-yellow-700">{error}</p>
        )}

        <div className="flex justify-end gap-3">
          <button
            onClick={onCancel}
            disabled={isPending}
            className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
          >
            Cancelar
          </button>
          <button
            onClick={handleConfirmar}
            disabled={isPending}
            className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
          >
            {isPending ? 'Cerrando...' : 'Confirmar cierre'}
          </button>
        </div>
      </div>
    </div>
  )
}
