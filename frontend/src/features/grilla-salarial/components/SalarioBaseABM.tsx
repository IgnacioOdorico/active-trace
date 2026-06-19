import { useState } from 'react'
import { useSalariosBase } from '../hooks/useGrillaSalarialApi'
import SalarioBaseForm from './SalarioBaseForm'
import type { SalarioBase } from '../types'

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

export default function SalarioBaseABM() {
  const { data, isLoading } = useSalariosBase()
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700">
          Salario Base
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          {showForm ? 'Cancelar' : '+ Nuevo salario base'}
        </button>
      </div>

      {showForm && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <SalarioBaseForm onSuccess={() => setShowForm(false)} />
        </div>
      )}

      {isLoading && (
        <div className="space-y-2">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="h-10 animate-pulse rounded bg-gray-200" />
          ))}
        </div>
      )}

      {!isLoading && data?.length === 0 && (
        <p className="py-4 text-center text-sm text-gray-500">
          No hay salarios base configurados.
        </p>
      )}

      {!isLoading && data && data.length > 0 && (
        <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Rol</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Monto</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Desde</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Hasta</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
            </tr>
          </thead>
          <tbody>
            {(data as SalarioBase[]).map((item) => (
              <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium text-gray-900">{item.rol}</td>
                <td className="px-4 py-2 text-right text-sm text-gray-700">
                  {formatARS(item.monto)}
                </td>
                <td className="px-4 py-2 text-center text-sm text-gray-600">{item.desde}</td>
                <td className="px-4 py-2 text-center text-sm text-gray-600">
                  {item.hasta ?? '—'}
                </td>
                <td className="px-4 py-2 text-center">
                  <span
                    className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      item.activo ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                    }`}
                  >
                    {item.activo ? 'Vigente' : 'Cerrado'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
