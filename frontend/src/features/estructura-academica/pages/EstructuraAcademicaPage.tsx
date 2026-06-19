import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import CarrerasABM from '../components/CarrerasABM'
import CohortesABM from '../components/CohortesABM'
import MateriasABM from '../components/MateriasABM'

type Tab = 'carreras' | 'cohortes' | 'materias'

export default function EstructuraAcademicaPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeGestionar = perms.includes('*:*') || perms.includes('estructura:gestionar')

  const [tab, setTab] = useState<Tab>('carreras')

  if (!puedeGestionar) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-sm text-red-700">
        Acceso denegado. No tenés el permiso <code>estructura:gestionar</code>.
      </div>
    )
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: 'carreras', label: 'Carreras' },
    { key: 'cohortes', label: 'Cohortes' },
    { key: 'materias', label: 'Materias' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Estructura Académica</h1>

      <div className="flex gap-2 border-b border-gray-200">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 text-sm font-medium ${
              tab === t.key
                ? 'border-b-2 border-blue-600 text-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'carreras' && <CarrerasABM />}
      {tab === 'cohortes' && <CohortesABM />}
      {tab === 'materias' && <MateriasABM />}
    </div>
  )
}
