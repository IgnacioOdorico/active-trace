import { useState } from 'react'
import MisTareas from '../components/MisTareas'
import TareasAdmin from '../components/TareasAdmin'
import CrearTareaForm from '../components/CrearTareaForm'
import HiloComentarios from '../components/HiloComentarios'
import type { Tarea } from '../types'

type Tab = 'mis-tareas' | 'admin'

export default function TareasPage() {
  const [tab, setTab] = useState<Tab>('mis-tareas')
  const [creando, setCreando] = useState(false)
  const [tareaDetalle, setTareaDetalle] = useState<Tarea | null>(null)

  return (
    <div className="mx-auto max-w-5xl py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Tareas</h1>
        <button
          type="button"
          onClick={() => setCreando(true)}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          + Nueva tarea
        </button>
      </div>

      <div className="mb-6 flex gap-4 border-b border-gray-200">
        <button
          type="button"
          onClick={() => setTab('mis-tareas')}
          className={`pb-2 text-sm font-medium ${
            tab === 'mis-tareas'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Mis Tareas
        </button>
        <button
          type="button"
          onClick={() => setTab('admin')}
          className={`pb-2 text-sm font-medium ${
            tab === 'admin'
              ? 'border-b-2 border-blue-600 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Administración Global
        </button>
      </div>

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        {tab === 'mis-tareas' && <MisTareas onVerDetalle={setTareaDetalle} />}
        {tab === 'admin' && <TareasAdmin onVerDetalle={setTareaDetalle} />}
      </div>

      {creando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-lg rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">Nueva Tarea</h2>
              <button
                type="button"
                onClick={() => setCreando(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <CrearTareaForm
              onSuccess={() => setCreando(false)}
              onCancel={() => setCreando(false)}
            />
          </div>
        </div>
      )}

      {tareaDetalle && (
        <HiloComentarios
          tarea={tareaDetalle}
          onCerrar={() => setTareaDetalle(null)}
        />
      )}
    </div>
  )
}
