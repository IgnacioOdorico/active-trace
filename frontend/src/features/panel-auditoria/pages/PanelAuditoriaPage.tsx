import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import FiltrosPanel from '../components/FiltrosPanel'
import AccionesPorDia from '../components/AccionesPorDia'
import ComunicacionesPorDocente from '../components/ComunicacionesPorDocente'
import InteraccionesDocenteMateria from '../components/InteraccionesDocenteMateria'
import UltimasAcciones from '../components/UltimasAcciones'
import type { PanelFilters } from '../types'
import { Button } from '../../../shared/components/ui/Button'
import { hasPermission } from '../../../shared/utils/permissions'

type Tab = 'acciones' | 'comunicaciones' | 'interacciones' | 'log'

export default function PanelAuditoriaPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeVer = hasPermission(perms, 'auditoria:ver') || hasPermission(perms, 'auditoria:ver(propio)')

  const [filters, setFilters] = useState<PanelFilters>({})
  const [tab, setTab] = useState<Tab>('acciones')

  if (!puedeVer) {
    return (
      <div className="rounded neo-latex-border bg-error-container p-6 text-center font-body-md text-on-error-container mt-8">
        Acceso denegado. No tenés el permiso <code className="font-mono-data text-on-error-container font-semibold">auditoria:ver</code>.
      </div>
    )
  }

  const tabs: { key: Tab; label: string }[] = [
    { key: 'acciones', label: 'Acciones por día' },
    { key: 'comunicaciones', label: 'Comunicaciones' },
    { key: 'interacciones', label: 'Interacciones' },
    { key: 'log', label: 'Log de acciones' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="font-headline-md text-headline-md text-on-surface">Panel de Auditoría</h1>

      <FiltrosPanel filters={filters} onChange={setFilters} />

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
        {tab === 'acciones' && <AccionesPorDia filters={filters} />}
        {tab === 'comunicaciones' && <ComunicacionesPorDocente filters={filters} />}
        {tab === 'interacciones' && <InteraccionesDocenteMateria filters={filters} />}
        {tab === 'log' && <UltimasAcciones filters={filters} />}
      </div>
    </div>
  )
}
