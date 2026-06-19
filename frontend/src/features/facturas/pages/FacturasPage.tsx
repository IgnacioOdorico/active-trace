import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import FacturasListado from '../components/FacturasListado'
import CargarFacturaForm from '../components/CargarFacturaForm'

export default function FacturasPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeVer = perms.includes('*:*') || perms.includes('facturas:ver')
  const puedeCargar = perms.includes('*:*') || perms.includes('facturas:cargar')
  const puedeAbonar = perms.includes('*:*') || perms.includes('facturas:abonar')

  const [showForm, setShowForm] = useState(false)

  if (!puedeVer) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-sm text-red-700">
        Acceso denegado. No tenés el permiso <code>facturas:ver</code>.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Facturas</h1>
        {puedeCargar && (
          <button
            onClick={() => setShowForm(!showForm)}
            className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            {showForm ? 'Cancelar carga' : '+ Cargar factura'}
          </button>
        )}
      </div>

      {showForm && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <h2 className="mb-3 text-sm font-semibold text-gray-700">Cargar nuevo comprobante</h2>
          <CargarFacturaForm onSuccess={() => setShowForm(false)} />
        </div>
      )}

      <FacturasListado puedeAbonar={puedeAbonar} />
    </div>
  )
}
