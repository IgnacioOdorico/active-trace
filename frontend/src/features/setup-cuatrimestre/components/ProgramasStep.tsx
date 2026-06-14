import { useRef } from 'react'
import { useProgramas, useSubirPrograma } from '../hooks/useProgramasApi'

export default function ProgramasStep() {
  const { data, isLoading } = useProgramas()
  const subirMutation = useSubirPrograma()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    const formData = new FormData()
    formData.append('archivo', file)
    // materia_id, carrera y cohorte se completarían con campos adicionales
    // en una implementación completa; aquí mostramos el patrón base
    subirMutation.mutate(formData)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const programas = data?.data ?? []

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <label className="cursor-pointer rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700">
          {subirMutation.isPending ? 'Subiendo...' : 'Subir programa'}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.doc,.docx"
            className="hidden"
            onChange={handleUpload}
            disabled={subirMutation.isPending}
          />
        </label>
        {subirMutation.isSuccess && (
          <span className="text-sm text-green-700">Programa subido correctamente.</span>
        )}
        {subirMutation.isError && (
          <span className="text-sm text-red-700">Error al subir el programa.</span>
        )}
      </div>

      {isLoading ? (
        <p className="text-sm text-gray-500">Cargando programas...</p>
      ) : programas.length === 0 ? (
        <p className="text-sm text-gray-400">Sin programas cargados aún.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                {['Materia', 'Carrera', 'Cohorte', 'Archivo'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-2 text-left text-xs font-semibold uppercase text-gray-500"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {programas.map((p) => (
                <tr key={p.id}>
                  <td className="px-4 py-2 text-sm text-gray-900">{p.materia_nombre}</td>
                  <td className="px-4 py-2 text-sm text-gray-600">{p.carrera}</td>
                  <td className="px-4 py-2 text-sm text-gray-600">{p.cohorte}</td>
                  <td className="px-4 py-2 text-sm">
                    {p.url ? (
                      <a
                        href={p.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {p.nombre_archivo ?? 'Ver'}
                      </a>
                    ) : (
                      <span className="text-gray-400">—</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
