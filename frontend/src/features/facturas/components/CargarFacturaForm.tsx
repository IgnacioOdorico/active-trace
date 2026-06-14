import { useRef, useState } from 'react'
import { useCargarFactura } from '../hooks/useFacturasApi'

interface Props {
  onSuccess: () => void
}

export default function CargarFacturaForm({ onSuccess }: Props) {
  const { mutate, isPending } = useCargarFactura()
  const [periodo, setPeriodo] = useState('')
  const [detalle, setDetalle] = useState('')
  const [archivo, setArchivo] = useState<File | null>(null)
  const [errors, setErrors] = useState<{ periodo?: string; detalle?: string; archivo?: string; root?: string }>({})
  const fileRef = useRef<HTMLInputElement>(null)

  function validate() {
    const e: typeof errors = {}
    if (!periodo) e.periodo = 'El período es requerido'
    if (!detalle.trim()) e.detalle = 'El detalle es requerido'
    if (!archivo) {
      e.archivo = 'El archivo es requerido'
    } else if (!archivo.name.toLowerCase().endsWith('.pdf')) {
      e.archivo = 'El archivo debe ser un PDF'
    }
    return e
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const errs = validate()
    setErrors(errs)
    if (Object.keys(errs).length > 0 || !archivo) return

    mutate(
      { periodo, detalle, archivo },
      {
        onSuccess: () => {
          setPeriodo('')
          setDetalle('')
          setArchivo(null)
          if (fileRef.current) fileRef.current.value = ''
          onSuccess()
        },
        onError: (err: unknown) => {
          const detail =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? ''
          setErrors((prev) => ({ ...prev, root: `Error: ${detail}` }))
        },
      },
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Período (AAAA-MM) *</label>
        <input
          type="month"
          value={periodo}
          onChange={(e) => setPeriodo(e.target.value)}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        {errors.periodo && <p className="text-xs text-red-600">{errors.periodo}</p>}
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Detalle *</label>
        <input
          type="text"
          value={detalle}
          onChange={(e) => setDetalle(e.target.value)}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          placeholder="Describí el comprobante"
        />
        {errors.detalle && <p className="text-xs text-red-600">{errors.detalle}</p>}
      </div>

      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Archivo PDF *</label>
        <input
          ref={fileRef}
          type="file"
          accept=".pdf"
          onChange={(e) => setArchivo(e.target.files?.[0] ?? null)}
          className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
        />
        {errors.archivo && <p className="text-xs text-red-600">{errors.archivo}</p>}
      </div>

      {errors.root && (
        <p className="rounded bg-red-50 p-2 text-xs text-red-700">{errors.root}</p>
      )}

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isPending}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {isPending ? 'Cargando...' : 'Cargar factura'}
        </button>
      </div>
    </form>
  )
}
