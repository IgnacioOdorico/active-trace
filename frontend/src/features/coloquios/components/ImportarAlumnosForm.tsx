import { useState } from 'react'
import { useImportarAlumnos } from '../hooks/useColoquiosApi'

interface ImportarAlumnosFormProps {
  convocatoriaId: string
  onSuccess: () => void
  onCancel: () => void
}

export default function ImportarAlumnosForm({
  convocatoriaId,
  onSuccess,
  onCancel,
}: ImportarAlumnosFormProps) {
  const [alumnoIdsText, setAlumnoIdsText] = useState('')
  const mutation = useImportarAlumnos()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const alumno_ids = alumnoIdsText
      .split('\n')
      .map((s) => s.trim())
      .filter(Boolean)

    if (alumno_ids.length === 0) return

    mutation.mutate(
      { id: convocatoriaId, payload: { alumno_ids } },
      { onSuccess },
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">
          IDs de alumnos habilitados (uno por línea)
        </label>
        <textarea
          rows={6}
          value={alumnoIdsText}
          onChange={(e) => setAlumnoIdsText(e.target.value)}
          placeholder="uuid-alumno-1&#10;uuid-alumno-2&#10;..."
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm font-mono"
        />
      </div>

      {mutation.isSuccess && (
        <div className="rounded-md bg-green-50 p-3 text-sm text-green-700">
          {mutation.data.importados} alumno(s) importados. Total convocados: {mutation.data.convocados}.
        </div>
      )}

      {mutation.isError && (
        <div className="rounded-md bg-red-50 p-3 text-sm text-red-700">
          Error al importar alumnos.
        </div>
      )}

      <div className="flex gap-3">
        <button
          type="submit"
          disabled={mutation.isPending || !alumnoIdsText.trim()}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {mutation.isPending ? 'Importando...' : 'Importar alumnos'}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Cancelar
        </button>
      </div>
    </form>
  )
}
