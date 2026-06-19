import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import CarrerasABM from '../components/CarrerasABM'
import CohortesABM from '../components/CohortesABM'
import MateriasABM from '../components/MateriasABM'
import { Button } from '../../../shared/components/ui/Button'
import { hasPermission } from '../../../shared/utils/permissions'

type Tab = 'carreras' | 'cohortes' | 'materias'

export default function EstructuraAcademicaPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeGestionar = hasPermission(perms, 'estructura:gestionar')

  const [tab, setTab] = useState<Tab>('carreras')

  if (!puedeGestionar) {
    return (
      <div className="rounded neo-latex-border bg-error-container p-6 text-center font-body-md text-on-error-container mt-8">
        Acceso denegado. No tenés el permiso <code className="font-mono-data text-on-error-container font-semibold">estructura:gestionar</code>.
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
      <h1 className="font-headline-md text-headline-md text-on-surface">Estructura Académica</h1>

      <div className="flex gap-2 border-b border-outline-variant pb-2">
        {tabs.map((t) => (
          <Button
            key={t.key}
            onClick={() => setTab(t.key)}
            variant={tab === t.key ? 'primary' : 'ghost'}
          >
            {t.label}
          </Button>
        ))}
      </div>

      <div>
        {tab === 'carreras' && <CarrerasABM />}
        {tab === 'cohortes' && <CohortesABM />}
        {tab === 'materias' && <MateriasABM />}
      </div>
    </div>
  )
}
