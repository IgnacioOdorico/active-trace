import { useState } from 'react'
import GestionAvisos from '../components/GestionAvisos'
import AvisosUsuario from '../components/AvisosUsuario'

type Tab = 'mis-avisos' | 'gestion'

export default function AvisosPage() {
  const [tab, setTab] = useState<Tab>('mis-avisos')

  return (
    <div className="mx-auto max-w-4xl py-8">
      <h1 className="mb-6 text-2xl font-bold text-gray-900">Avisos</h1>

      <div className="mb-6 flex gap-4 border-b border-gray-200">
        <button
          type="button"
          onClick={() => setTab('mis-avisos')}
          className={`pb-2 text-sm font-medium ${
            tab === 'mis-avisos'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Mis avisos
        </button>
        <button
          type="button"
          onClick={() => setTab('gestion')}
          className={`pb-2 text-sm font-medium ${
            tab === 'gestion'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Gestión
        </button>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        {tab === 'mis-avisos' && <AvisosUsuario />}
        {tab === 'gestion' && <GestionAvisos />}
      </div>
    </div>
  )
}
