import { useRef, useState } from 'react'
import { useCargarFactura } from '../hooks/useFacturasApi'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

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
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Período (AAAA-MM) *</label>
          <Input
            type="month"
            value={periodo}
            onChange={(e) => setPeriodo(e.target.value)}
            className="w-full"
          />
          {errors.periodo && <p className="mt-1 font-body-md text-[12px] text-error">{errors.periodo}</p>}
        </div>

        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Detalle *</label>
          <Input
            type="text"
            value={detalle}
            onChange={(e) => setDetalle(e.target.value)}
            className="w-full"
            placeholder="Describí el comprobante"
          />
          {errors.detalle && <p className="mt-1 font-body-md text-[12px] text-error">{errors.detalle}</p>}
        </div>
      </div>

      <div className="flex flex-col gap-1">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Archivo PDF *</label>
        <Input
          ref={fileRef}
          type="file"
          accept=".pdf"
          onChange={(e) => setArchivo(e.target.files?.[0] ?? null)}
          className="w-full"
        />
        {errors.archivo && <p className="mt-1 font-body-md text-[12px] text-error">{errors.archivo}</p>}
      </div>

      {errors.root && (
        <p className="rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">{errors.root}</p>
      )}

      <div className="flex justify-end pt-4 border-t border-outline-variant">
        <Button
          type="submit"
          disabled={isPending}
          variant="primary"
        >
          {isPending ? 'Cargando...' : 'Cargar factura'}
        </Button>
      </div>
    </form>
  )
}
