import { useState } from 'react'
import { useSalariosPlus } from '../hooks/useGrillaSalarialApi'
import SalarioPlusForm from './SalarioPlusForm'
import type { SalarioPlus } from '../types'

function formatARS(amount: number) {
  return new Intl.NumberFormat('es-AR', { style: 'currency', currency: 'ARS' }).format(amount)
}

export default function SalarioPlusABM() {
  const { data, isLoading } = useSalariosPlus()
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700">
          Salario Plus
        </h3>
        <button
          onClick={() => setShowForm(!showForm)}
          className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          {showForm ? 'Cancelar' : '+ Nuevo plus'}
        </button>
      </div>

      {showForm && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <SalarioPlusForm onSuccess={() => setShowForm(false)} />
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
        <p className="py-4 text-center text-sm text-gray-500">No hay plus salariales configurados.</p>
      )}

      {!isLoading && data && data.length > 0 && (
        <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Grupo</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Rol</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Descripción</th>
              <th className="px-4 py-2 text-right text-xs font-medium text-gray-500">Monto</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Desde</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Hasta</th>
            </tr>
          </thead>
          <tbody>
            {(data as SalarioPlus[]).map((item) => (
              <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium text-gray-900">{item.grupo}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{item.rol}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{item.descripcion}</td>
                <td className="px-4 py-2 text-right text-sm text-gray-700">
                  {formatARS(item.monto)}
                </td>
                <td className="px-4 py-2 text-center text-sm text-gray-600">{item.desde}</td>
                <td className="px-4 py-2 text-center text-sm text-gray-600">
                  {item.hasta ?? '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
