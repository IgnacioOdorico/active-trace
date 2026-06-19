import { useState } from 'react'
import { useSalariosBase } from '../hooks/useGrillaSalarialApi'
import SalarioBaseForm from './SalarioBaseForm'
import type { SalarioBase } from '../types'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

export default function SalarioBaseABM() {
  const { data, isLoading } = useSalariosBase()
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-headline-sm text-headline-sm text-on-surface">
          Salario Base
        </h3>
        <Button
          onClick={() => setShowForm(!showForm)}
          variant={showForm ? 'secondary' : 'primary'}
        >
          {showForm ? 'Cancelar' : '+ Nuevo salario base'}
        </Button>
      </div>

      {showForm && (
        <div className="rounded neo-latex-border bg-surface-container-high p-4">
          <SalarioBaseForm onSuccess={() => setShowForm(false)} />
        </div>
      )}

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-10 animate-pulse rounded bg-surface-container" />
          ))}
        </div>
      )}

      {!isLoading && data?.length === 0 && (
        <p className="py-4 text-center font-body-md text-on-surface-variant">
          No hay salarios base configurados.
        </p>
      )}

      {!isLoading && data && data.length > 0 && (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Rol</th>
                <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Monto</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Desde</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Hasta</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {(data as SalarioBase[]).map((item) => (
                <tr key={item.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{item.rol}</td>
                  <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface">
                    {formatARS(item.monto)}
                  </td>
                  <td className="px-4 py-3 text-center font-mono-data text-mono-data text-on-surface-variant">{item.desde}</td>
                  <td className="px-4 py-3 text-center font-mono-data text-mono-data text-on-surface-variant">
                    {item.hasta ?? '—'}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant={item.activo ? 'success' : 'neutral'}>
                      {item.activo ? 'Vigente' : 'Cerrado'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
