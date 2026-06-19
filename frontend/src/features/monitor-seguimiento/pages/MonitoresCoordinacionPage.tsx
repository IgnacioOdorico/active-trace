import { useState } from 'react'
import MonitorGeneral from '../components/MonitorGeneral'
import MonitorSeguimiento from '../components/MonitorSeguimiento'
import { Button } from '../../../shared/components/ui/Button'

type Tab = 'general' | 'seguimiento'

/**
 * Vista de monitores transversales para coordinación/admin.
 * Reutiliza MonitorGeneral (F2.7) y MonitorSeguimiento (F2.9) de C-22.
 * MonitorSeguimiento ya expone fecha_desde/fecha_hasta para roles coordinador.
 * Acceso protegido por permiso monitores:ver (via Layout + ProtectedRoute).
 */
export default function MonitoresCoordinacionPage() {
  const [tab, setTab] = useState<Tab>('general')

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">Monitores — Coordinación</h1>
        <p className="mt-1 font-body-md text-on-surface-variant">
          Vista transversal del tenant para supervisión de alumnos y seguimiento docente.
        </p>
      </div>

      <div className="flex gap-2 mb-6 border-b border-outline-variant pb-2">
        <Button
          onClick={() => setTab('general')}
          variant={tab === 'general' ? 'primary' : 'ghost'}
        >
          Monitor General (F2.7)
        </Button>
        <Button
          onClick={() => setTab('seguimiento')}
          variant={tab === 'seguimiento' ? 'primary' : 'ghost'}
        >
          Seguimiento con Rango de Fechas (F2.9)
        </Button>
      </div>

      <div>
        {tab === 'general' && <MonitorGeneral />}
        {tab === 'seguimiento' && <MonitorSeguimiento />}
      </div>
    </div>
  )
}
