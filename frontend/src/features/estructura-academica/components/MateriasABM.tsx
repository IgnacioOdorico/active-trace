import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { materiaSchema, type MateriaFormValues } from '../schemas'
import { useMateriasAdmin, useCrearMateria } from '../hooks/useEstructuraApi'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'

function MateriaForm({ onSuccess }: { onSuccess: () => void }) {
  const { mutate, isPending } = useCrearMateria()
  const { register, handleSubmit, setError, formState: { errors } } = useForm<MateriaFormValues>({
    resolver: zodResolver(materiaSchema),
  })

  function onSubmit(values: MateriaFormValues) {
    mutate(
      { ...values, carrera_id: values.carrera_id || null },
      {
        onSuccess,
        onError: (err: unknown) => {
          const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? ''
          setError('root', { message: `Error: ${detail}` })
        },
      },
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Código *</label>
          <Input {...register('codigo')} />
          {errors.codigo && <p className="font-body-md text-[12px] text-on-error-container mt-1">{errors.codigo.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Nombre *</label>
          <Input {...register('nombre')} />
          {errors.nombre && <p className="font-body-md text-[12px] text-on-error-container mt-1">{errors.nombre.message}</p>}
        </div>
      </div>
      <div className="flex flex-col gap-1">
        <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Descripción</label>
        <Input {...register('descripcion')} />
      </div>
      {errors.root && <p className="rounded neo-latex-border bg-error-container p-2 font-body-md text-[12px] text-on-error-container">{errors.root.message}</p>}
      <div className="flex justify-end pt-2">
        <Button type="submit" disabled={isPending} variant="primary">
          {isPending ? 'Guardando...' : 'Crear materia'}
        </Button>
      </div>
    </form>
  )
}

export default function MateriasABM() {
  const { data, isLoading } = useMateriasAdmin()
  const [showForm, setShowForm] = useState(false)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mt-4">
        <h3 className="font-headline-sm text-headline-sm text-on-surface">Materias</h3>
        <Button onClick={() => setShowForm(!showForm)} variant={showForm ? 'secondary' : 'primary'}>
          {showForm ? 'Cancelar' : '+ Nueva materia'}
        </Button>
      </div>
      {showForm && (
        <div className="rounded neo-latex-border bg-surface-container-lowest p-5">
          <MateriaForm onSuccess={() => setShowForm(false)} />
        </div>
      )}
      {isLoading && <div className="h-20 animate-pulse rounded neo-latex-border bg-surface-container" />}
      {!isLoading && data?.length === 0 && (
        <p className="py-6 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border">No hay materias registradas.</p>
      )}
      {!isLoading && data && data.length > 0 && (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Código</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Descripción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {data.map((m) => (
                <tr key={m.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-mono-data text-mono-data font-semibold text-on-surface">{m.codigo}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{m.nombre}</td>
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface-variant">{m.descripcion ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
