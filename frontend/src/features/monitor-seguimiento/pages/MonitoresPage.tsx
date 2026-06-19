import { useState } from 'react'
import MonitorGeneral from '../components/MonitorGeneral'
import MonitorSeguimiento from '../components/MonitorSeguimiento'
import { Button } from '../../../shared/components/ui/Button'

type Tab = 'general' | 'seguimiento'

export default function MonitoresPage() {
  const [tab, setTab] = useState<Tab>('general')

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Monitores</h1>
      </div>

      <div className="flex gap-2 mb-6 border-b border-outline-variant pb-2">
        <Button
          onClick={() => setTab('general')}
          variant={tab === 'general' ? 'primary' : 'ghost'}
        >
          General
        </Button>
        <Button
          onClick={() => setTab('seguimiento')}
          variant={tab === 'seguimiento' ? 'primary' : 'ghost'}
        >
          Seguimiento
        </Button>
      </div>

      <div>
        {tab === 'general' && <MonitorGeneral />}
        {tab === 'seguimiento' && <MonitorSeguimiento />}
      </div>
    </div>
  )
}
