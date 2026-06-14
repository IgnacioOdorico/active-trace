import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import SalarioBaseABM from '../components/SalarioBaseABM'
import SalarioPlusABM from '../components/SalarioPlusABM'

type Tab = 'base' | 'plus'

export default function GrillaSalarialPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeConfigurar =
    perms.includes('*:*') || perms.includes('liquidaciones:configurar-salarios')

  const [tab, setTab] = useState<Tab>('base')

  if (!puedeConfigurar) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-sm text-red-700">
        Acceso denegado. No tenés el permiso{' '}
        <code>liquidaciones:configurar-salarios</code>.
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Grilla Salarial</h1>

      <div className="flex gap-2 border-b border-gray-200">
        {(['base', 'plus'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium ${
              tab === t
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {t === 'base' ? 'Salario Base' : 'Salario Plus'}
          </button>
        ))}
      </div>

      {tab === 'base' && <SalarioBaseABM />}
      {tab === 'plus' && <SalarioPlusABM />}
    </div>
  )
}
