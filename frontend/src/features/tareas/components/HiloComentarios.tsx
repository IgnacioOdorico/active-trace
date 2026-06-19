import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { comentarioSchema, type ComentarioFormData } from '../schemas'
import { useComentarios, useAgregarComentario } from '../hooks/useTareasApi'
import type { Tarea } from '../types'
import { Button } from '../../../shared/components/ui/Button'

interface HiloComentariosProps {
  tarea: Tarea
  onCerrar: () => void
}

export default function HiloComentarios({ tarea, onCerrar }: HiloComentariosProps) {
  const { data, isLoading } = useComentarios(tarea.id)
  const agregarComentario = useAgregarComentario(tarea.id)
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<ComentarioFormData>({
    resolver: zodResolver(comentarioSchema),
  })

  const comentarios = data?.items ?? []

  const onSubmit = (values: ComentarioFormData) => {
    agregarComentario.mutate(values, { onSuccess: () => reset() })
  }

  return (
    <div className="flex flex-col h-full max-h-[70vh]">
      <div className="flex items-center justify-between border-b border-outline-variant pb-4 mb-4">
        <div>
          <h2 className="font-headline-sm text-headline-sm text-on-surface">{tarea.descripcion}</h2>
          <p className="font-mono-data text-[12px] text-on-surface-variant mt-1">
            {tarea.asignado_por} → {tarea.asignado_a}
          </p>
        </div>
        <button
          type="button"
          onClick={onCerrar}
          className="text-on-surface-variant hover:text-on-surface transition-colors self-start"
        >
          ✕
        </button>
      </div>

      <div className="flex-1 overflow-y-auto mb-4 min-h-[200px]">
        {isLoading && <p className="font-body-md text-on-surface-variant text-center py-4">Cargando comentarios...</p>}
        {!isLoading && comentarios.length === 0 && (
          <p className="font-body-md text-on-surface-variant text-center py-4">Sin comentarios aún.</p>
        )}
        <div className="space-y-4">
          {comentarios.map((c) => (
            <div key={c.id} className="rounded neo-latex-border bg-surface-container-lowest p-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="font-label-caps text-[12px] font-semibold text-on-surface">{c.autor_id}</span>
                <span className="font-mono-data text-[12px] text-on-surface-variant/70">
                  {new Date(c.creado_at).toLocaleString('es-AR')}
                </span>
              </div>
              <p className="font-body-md text-body-md text-on-surface whitespace-pre-wrap">{c.texto}</p>
            </div>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="border-t border-outline-variant pt-4 mt-auto">
        <div className="flex gap-3">
          <textarea
            {...register('texto')}
            rows={2}
            placeholder="Agregar comentario..."
            className="flex-1 rounded neo-latex-border bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary resize-none"
          />
          <Button
            type="submit"
            disabled={agregarComentario.isPending}
            variant="primary"
            className="self-end"
          >
            Enviar
          </Button>
        </div>
        {errors.texto && (
          <p className="mt-1 font-body-md text-[12px] text-on-error-container">{errors.texto.message}</p>
        )}
      </form>
    </div>
  )
}
