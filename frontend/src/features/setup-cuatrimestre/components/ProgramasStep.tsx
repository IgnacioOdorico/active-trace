import { useRef } from 'react'
import { useProgramas, useSubirPrograma } from '../hooks/useProgramasApi'
import { Button } from '../../../shared/components/ui/Button'

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
        <label className="cursor-pointer">
          <Button
            as="span"
            variant="primary"
            disabled={subirMutation.isPending}
          >
            {subirMutation.isPending ? 'Subiendo...' : 'Subir programa'}
          </Button>
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
          <span className="font-body-md text-on-success-container">Programa subido correctamente.</span>
        )}
        {subirMutation.isError && (
          <span className="font-body-md text-on-error-container">Error al subir el programa.</span>
        )}
      </div>

      {isLoading ? (
        <p className="font-body-md text-on-surface-variant">Cargando programas...</p>
      ) : programas.length === 0 ? (
        <p className="font-body-md text-on-surface-variant">Sin programas cargados aún.</p>
      ) : (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                {['Materia', 'Carrera', 'Cohorte', 'Archivo'].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {programas.map((p) => (
                <tr key={p.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{p.materia_nombre}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{p.carrera}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{p.cohorte}</td>
                  <td className="px-4 py-3 font-body-md text-[12px]">
                    {p.url ? (
                      <a
                        href={p.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-primary hover:underline font-medium"
                      >
                        {p.nombre_archivo ?? 'Ver'}
                      </a>
                    ) : (
                      <span className="text-on-surface-variant">—</span>
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
