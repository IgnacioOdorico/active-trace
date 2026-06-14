import { useState } from 'react'
import EncuentrosTransversal from '../components/EncuentrosTransversal'
import GestionGuardias from '../components/GestionGuardias'

type Tab = 'encuentros' | 'guardias'

export default function EncuentrosAdminPage() {
  const [tab, setTab] = useState<Tab>('encuentros')

  return (
    <div className="mx-auto max-w-7xl py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Encuentros y Guardias</h1>

      <div className="mb-6 flex gap-4 border-b border-gray-200">
        <button
          type="button"
          onClick={() => setTab('encuentros')}
          className={`pb-2 text-sm font-medium ${
            tab === 'encuentros'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Vista transversal de encuentros
        </button>
        <button
          type="button"
          onClick={() => setTab('guardias')}
          className={`pb-2 text-sm font-medium ${
            tab === 'guardias'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Registro de guardias
        </button>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        {tab === 'encuentros' && <EncuentrosTransversal />}
        {tab === 'guardias' && <GestionGuardias />}
      </div>
    </div>
  )
}
