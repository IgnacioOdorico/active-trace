import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import SalarioBaseABM from '../components/SalarioBaseABM'
import SalarioPlusABM from '../components/SalarioPlusABM'
import { Button } from '../../../shared/components/ui/Button'

type Tab = 'base' | 'plus'

export default function GrillaSalarialPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeConfigurar =
    perms.includes('*:*') || perms.includes('liquidaciones:configurar-salarios')

  const [tab, setTab] = useState<Tab>('base')

  if (!puedeConfigurar) {
    return (
      <div className="rounded neo-latex-border bg-error-container p-6 text-center font-body-md text-on-error-container">
        Acceso denegado. No tenés el permiso{' '}
        <code className="font-mono-data bg-white/50 px-1 rounded">liquidaciones:configurar-salarios</code>.
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Grilla Salarial</h1>
      </div>

      <div className="flex gap-2 mb-6 border-b border-outline-variant pb-2">
        {(['base', 'plus'] as const).map((t) => (
          <Button
            key={t}
            onClick={() => setTab(t)}
            variant={tab === t ? 'primary' : 'ghost'}
          >
            {t === 'base' ? 'Salario Base' : 'Salario Plus'}
          </Button>
        ))}
      </div>

      <div>
        {tab === 'base' && <SalarioBaseABM />}
        {tab === 'plus' && <SalarioPlusABM />}
      </div>
    </div>
  )
}
