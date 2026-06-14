import { useState } from 'react'
import MonitorGeneral from '../components/MonitorGeneral'
import MonitorSeguimiento from '../components/MonitorSeguimiento'

type Tab = 'general' | 'seguimiento'

export default function MonitoresPage() {
  const [tab, setTab] = useState<Tab>('general')

  return (
    <div className="mx-auto max-w-7xl py-8">
      <h1 className="text-2xl font-bold text-gray-900">Monitores</h1>

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
          General
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
          Seguimiento
        </button>
      </div>

      <div className="mt-6">
        {tab === 'general' && <MonitorGeneral />}
        {tab === 'seguimiento' && <MonitorSeguimiento />}
      </div>
    </div>
  )
}
