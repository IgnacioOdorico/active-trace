import { useState } from 'react'
import MisEquipos from '../components/MisEquipos'
import AsignacionMasivaForm from '../components/AsignacionMasivaForm'
import ClonarEquipoForm from '../components/ClonarEquipoForm'
import { VigenciaIndividualForm, VigenciaMasivaForm } from '../components/VigenciaForm'
import type { MiEquipo } from '../types'

type Panel = 'listado' | 'asignacion' | 'clonar' | 'vigencia-masiva'

export default function EquiposPage() {
  const [panel, setPanel] = useState<Panel>('listado')
  const [equipoVigencia, setEquipoVigencia] = useState<MiEquipo | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  const handleVigenciaOpen = (equipo: MiEquipo) => {
    setEquipoVigencia(equipo)
  }

  const handleVigenciaClose = () => {
    setEquipoVigencia(null)
    setSuccessMsg('Vigencia actualizada correctamente.')
    setTimeout(() => setSuccessMsg(null), 3000)
  }

  return (
    <div className="mx-auto max-w-7xl py-8">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Equipos Docentes</h1>
        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setPanel('listado')}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              panel === 'listado' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Mis Equipos
          </button>
          <button
            type="button"
            onClick={() => setPanel('asignacion')}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              panel === 'asignacion' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Asignación Masiva
          </button>
          <button
            type="button"
            onClick={() => setPanel('clonar')}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              panel === 'clonar' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Clonar Equipo
          </button>
          <button
            type="button"
            onClick={() => setPanel('vigencia-masiva')}
            className={`rounded-md px-3 py-2 text-sm font-medium ${
              panel === 'vigencia-masiva' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Vigencia Masiva
          </button>
        </div>
      </div>

      {successMsg && (
        <div className="mb-4 rounded-md bg-green-50 p-3 text-sm text-green-700">{successMsg}</div>
      )}

      <div className="rounded-lg border border-gray-200 bg-white p-6">
        {panel === 'listado' && (
          <MisEquipos onVigencia={handleVigenciaOpen} />
        )}
        {panel === 'asignacion' && (
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-800">Asignación Masiva</h2>
            <AsignacionMasivaForm
              onSuccess={(ids) => {
                setSuccessMsg(`${ids.length} asignaciones creadas.`)
                setPanel('listado')
                setTimeout(() => setSuccessMsg(null), 4000)
              }}
            />
          </div>
        )}
        {panel === 'clonar' && (
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-800">Clonar Equipo</h2>
            <ClonarEquipoForm
              onSuccess={() => {
                setSuccessMsg('Equipo clonado correctamente.')
                setPanel('listado')
                setTimeout(() => setSuccessMsg(null), 4000)
              }}
            />
          </div>
        )}
        {panel === 'vigencia-masiva' && (
          <div>
            <h2 className="mb-4 text-lg font-semibold text-gray-800">Modificar Vigencia Masiva</h2>
            <VigenciaMasivaForm
              onSuccess={(filas) => {
                setSuccessMsg(`${filas} fila(s) afectada(s).`)
                setTimeout(() => setSuccessMsg(null), 4000)
              }}
            />
          </div>
        )}
      </div>

      {equipoVigencia && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">Modificar Vigencia</h2>
              <button
                type="button"
                onClick={() => setEquipoVigencia(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            <VigenciaIndividualForm equipo={equipoVigencia} onSuccess={handleVigenciaClose} />
          </div>
        </div>
      )}
    </div>
  )
}
