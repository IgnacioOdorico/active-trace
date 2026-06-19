import { useState } from 'react'
import MonitorGeneral from '../components/MonitorGeneral'
import MonitorSeguimiento from '../components/MonitorSeguimiento'

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
    <div className="mx-auto max-w-7xl py-8">
      <h1 className="text-2xl font-bold text-gray-900">Monitores — Coordinación</h1>
      <p className="mt-1 text-sm text-gray-500">
        Vista transversal del tenant para supervisión de alumnos y seguimiento docente.
      </p>

      <div className="mt-6 flex gap-4 border-b border-gray-200">
        <button
          type="button"
          onClick={() => setTab('general')}
          className={`pb-2 text-sm font-medium ${
            tab === 'general'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Monitor General (F2.7)
        </button>
        <button
          type="button"
          onClick={() => setTab('seguimiento')}
          className={`pb-2 text-sm font-medium ${
            tab === 'seguimiento'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Seguimiento con Rango de Fechas (F2.9)
        </button>
      </div>

      <div className="mt-6">
        {tab === 'general' && <MonitorGeneral />}
        {tab === 'seguimiento' && <MonitorSeguimiento />}
      </div>
    </div>
  )
}
