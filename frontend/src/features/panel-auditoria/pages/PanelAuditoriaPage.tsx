import { useState } from 'react'
import { useAuth } from '../../auth/hooks/useAuth'
import FiltrosPanel from '../components/FiltrosPanel'
import AccionesPorDia from '../components/AccionesPorDia'
import ComunicacionesPorDocente from '../components/ComunicacionesPorDocente'
import InteraccionesDocenteMateria from '../components/InteraccionesDocenteMateria'
import UltimasAcciones from '../components/UltimasAcciones'
import type { PanelFilters } from '../types'

type Tab = 'acciones' | 'comunicaciones' | 'interacciones' | 'log'

export default function PanelAuditoriaPage() {
  const { user } = useAuth()
  const perms = user?.permissions ?? []
  const puedeVer =
    perms.includes('*:*') ||
    perms.includes('auditoria:ver') ||
    perms.includes('auditoria:ver(propio)')

  const [filters, setFilters] = useState<PanelFilters>({})
  const [tab, setTab] = useState<Tab>('acciones')

  if (!puedeVer) {
    return (
      <div className="rounded-lg bg-red-50 p-6 text-center text-sm text-red-700">
        Acceso denegado. No tenés el permiso <code>auditoria:ver</code>.
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
      <h1 className="text-2xl font-bold text-gray-900">Panel de Auditoría</h1>

      <FiltrosPanel filters={filters} onChange={setFilters} />

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

      {tab === 'acciones' && <AccionesPorDia filters={filters} />}
      {tab === 'comunicaciones' && <ComunicacionesPorDocente filters={filters} />}
      {tab === 'interacciones' && <InteraccionesDocenteMateria filters={filters} />}
      {tab === 'log' && <UltimasAcciones filters={filters} />}
    </div>
  )
}
