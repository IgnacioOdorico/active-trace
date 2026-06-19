import { useState } from 'react'
import { useImportarAlumnos } from '../hooks/useColoquiosApi'
import { Button } from '../../../shared/components/ui/Button'

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
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="flex flex-col gap-1">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">
          IDs de alumnos habilitados (uno por línea)
        </label>
        <textarea
          rows={6}
          value={alumnoIdsText}
          onChange={(e) => setAlumnoIdsText(e.target.value)}
          placeholder="uuid-alumno-1&#10;uuid-alumno-2&#10;..."
          className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-mono-data text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>

      {mutation.isSuccess && (
        <div className="rounded neo-latex-border bg-success-container/20 p-3 font-body-md text-success">
          {mutation.data.cantidad_importados} alumno(s) importados.
        </div>
      )}

      {mutation.isError && (
        <div className="rounded neo-latex-border bg-error-container p-3 font-body-md text-on-error-container">
          Error al importar alumnos.
        </div>
      )}

      <div className="flex gap-3 pt-4 border-t border-outline-variant">
        <Button
          type="submit"
          disabled={mutation.isPending || !alumnoIdsText.trim()}
          variant="primary"
        >
          {mutation.isPending ? 'Importando...' : 'Importar alumnos'}
        </Button>
        <Button
          type="button"
          onClick={onCancel}
          variant="secondary"
        >
          Cancelar
        </Button>
      </div>
    </form>
  )
}
