import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { comentarioSchema, type ComentarioFormData } from '../schemas'
import { useComentarios, useAgregarComentario } from '../hooks/useTareasApi'
import type { Tarea } from '../types'

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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="flex w-full max-w-lg flex-col rounded-lg bg-white shadow-xl" style={{ maxHeight: '80vh' }}>
        <div className="flex items-center justify-between border-b border-gray-200 p-4">
          <div>
            <h2 className="font-semibold text-gray-900">{tarea.descripcion}</h2>
            <p className="text-xs text-gray-500">
              {tarea.asignado_por} → {tarea.asignado_a}
            </p>
          </div>
          <button
            type="button"
            onClick={onCerrar}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {isLoading && <p className="text-sm text-gray-500">Cargando comentarios...</p>}
          {!isLoading && comentarios.length === 0 && (
            <p className="text-sm text-gray-400">Sin comentarios aún.</p>
          )}
          <div className="space-y-3">
            {comentarios.map((c) => (
              <div key={c.id} className="rounded-lg bg-gray-50 p-3">
                <div className="mb-1 flex items-center gap-2">
                  <span className="text-xs font-medium text-gray-700">{c.autor_id}</span>
                  <span className="text-xs text-gray-400">
                    {new Date(c.creado_at).toLocaleString('es-AR')}
                  </span>
                </div>
                <p className="text-sm text-gray-700">{c.texto}</p>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="border-t border-gray-200 p-4">
          <div className="flex gap-2">
            <textarea
              {...register('texto')}
              rows={2}
              placeholder="Agregar comentario..."
              className="flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={agregarComentario.isPending}
              className="self-end rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              Enviar
            </button>
          </div>
          {errors.texto && (
            <p className="mt-1 text-xs text-red-600">{errors.texto.message}</p>
          )}
        </form>
      </div>
    </div>
  )
}
