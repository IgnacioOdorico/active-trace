import { useState } from 'react'
import { useSalariosPlus } from '../hooks/useGrillaSalarialApi'
import SalarioPlusForm from './SalarioPlusForm'
import type { SalarioPlus } from '../types'
import { Button } from '../../../shared/components/ui/Button'

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

export default function SalarioPlusABM() {
  const { data, isLoading } = useSalariosPlus()
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-headline-sm text-headline-sm text-on-surface">
          Salario Plus
        </h3>
        <Button
          onClick={() => setShowForm(!showForm)}
          variant={showForm ? 'secondary' : 'primary'}
        >
          {showForm ? 'Cancelar' : '+ Nuevo plus'}
        </Button>
      </div>

      {showForm && (
        <div className="rounded neo-latex-border bg-surface-container-high p-4">
          <SalarioPlusForm onSuccess={() => setShowForm(false)} />
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
        <p className="py-4 text-center font-body-md text-on-surface-variant">No hay plus salariales configurados.</p>
      )}

      {!isLoading && data && data.length > 0 && (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Grupo</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Rol</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Descripción</th>
                <th className="px-4 py-3 text-right font-label-caps text-label-caps uppercase text-on-surface-variant">Monto</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Desde</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Hasta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {(data as SalarioPlus[]).map((item) => (
                <tr key={item.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{item.grupo}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{item.rol}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{item.descripcion}</td>
                  <td className="px-4 py-3 text-right font-mono-data text-mono-data text-on-surface">
                    {formatARS(item.monto)}
                  </td>
                  <td className="px-4 py-3 text-center font-mono-data text-mono-data text-on-surface-variant">{item.desde}</td>
                  <td className="px-4 py-3 text-center font-mono-data text-mono-data text-on-surface-variant">
                    {item.hasta ?? '—'}
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
