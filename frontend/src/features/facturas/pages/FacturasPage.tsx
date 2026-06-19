import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import FacturasListado from '../components/FacturasListado'
import CargarFacturaForm from '../components/CargarFacturaForm'
import { Button } from '../../../shared/components/ui/Button'

export default function FacturasPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeVer = perms.includes('*:*') || perms.includes('facturas:ver')
  const puedeCargar = perms.includes('*:*') || perms.includes('facturas:cargar')
  const puedeAbonar = perms.includes('*:*') || perms.includes('facturas:abonar')

  const [showForm, setShowForm] = useState(false)

  if (!puedeVer) {
    return (
      <div className="rounded neo-latex-border bg-error-container p-6 text-center font-body-md text-on-error-container">
        Acceso denegado. No tenés el permiso <code className="font-mono-data bg-white/50 px-1 rounded">facturas:ver</code>.
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Facturas</h1>
        {puedeCargar && (
          <Button
            onClick={() => setShowForm(!showForm)}
            variant={showForm ? 'secondary' : 'primary'}
          >
            {showForm ? 'Cancelar carga' : '+ Cargar factura'}
          </Button>
        )}
      </div>

      {showForm && (
        <div className="rounded neo-latex-border bg-surface-container-high p-4">
          <h2 className="mb-4 font-headline-sm text-headline-sm text-on-surface">Cargar nuevo comprobante</h2>
          <CargarFacturaForm onSuccess={() => setShowForm(false)} />
        </div>
      )}

      <FacturasListado puedeAbonar={puedeAbonar} />
    </div>
  )
}
