import { useState } from 'react'
import EncuentrosTransversal from '../components/EncuentrosTransversal'
import GestionGuardias from '../components/GestionGuardias'
import { Button } from '../../../shared/components/ui/Button'

type Tab = 'encuentros' | 'guardias'

export default function EncuentrosAdminPage() {
  const [tab, setTab] = useState<Tab>('encuentros')

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Encuentros y Guardias</h1>
      </div>

      <div className="flex gap-2 mb-6 border-b border-outline-variant pb-2">
        <Button
          onClick={() => setTab('encuentros')}
          variant={tab === 'encuentros' ? 'primary' : 'ghost'}
        >
          Vista transversal de encuentros
        </Button>
        <Button
          onClick={() => setTab('guardias')}
          variant={tab === 'guardias' ? 'primary' : 'ghost'}
        >
          Registro de guardias
        </Button>
      </div>

      <div>
        {tab === 'encuentros' && <EncuentrosTransversal />}
        {tab === 'guardias' && <GestionGuardias />}
      </div>
    </div>
  )
}
