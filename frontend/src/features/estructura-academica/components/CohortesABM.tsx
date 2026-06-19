import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { cohorteSchema, type CohorteFormValues } from '../schemas'
import { useCarreras, useCohortes, useCrearCohorte, useActualizarCohorte } from '../hooks/useEstructuraApi'
import type { Cohorte } from '../types'
import { Button } from '../../../shared/components/ui/Button'
import { Badge } from '../../../shared/components/ui/Badge'
import { Input } from '../../../shared/components/ui/Input'

function CohorteForm({ onSuccess }: { onSuccess: () => void }) {
  const { data: carreras } = useCarreras()
  const { mutate, isPending } = useCrearCohorte()
  const { register, handleSubmit, setError, formState: { errors } } = useForm<CohorteFormValues>({
    resolver: zodResolver(cohorteSchema),
  })

  function onSubmit(values: CohorteFormValues) {
    mutate(
      { ...values, fecha_inicio: values.fecha_inicio || null, fecha_fin: values.fecha_fin || null },
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
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Nombre *</label>
          <Input {...register('nombre')} placeholder="Ej: 2024-1" />
          {errors.nombre && <p className="font-body-md text-[12px] text-on-error-container mt-1">{errors.nombre.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Carrera *</label>
          <select {...register('carrera_id')} className="rounded neo-latex-border bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary w-full">
            <option value="">Seleccioná</option>
            {carreras?.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
          </select>
          {errors.carrera_id && <p className="font-body-md text-[12px] text-on-error-container mt-1">{errors.carrera_id.message}</p>}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Fecha inicio</label>
          <Input type="date" {...register('fecha_inicio')} />
        </div>
        <div className="flex flex-col gap-1">
          <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Fecha fin</label>
          <Input type="date" {...register('fecha_fin')} />
          {errors.fecha_fin && <p className="font-body-md text-[12px] text-on-error-container mt-1">{errors.fecha_fin.message}</p>}
        </div>
      </div>
      {errors.root && <p className="rounded neo-latex-border bg-error-container p-2 font-body-md text-[12px] text-on-error-container">{errors.root.message}</p>}
      <div className="flex justify-end pt-2">
        <Button type="submit" disabled={isPending} variant="primary">
          {isPending ? 'Guardando...' : 'Crear cohorte'}
        </Button>
      </div>
    </form>
  )
}

export default function CohortesABM() {
  const { data, isLoading } = useCohortes()
  const { mutate: actualizar } = useActualizarCohorte()
  const [showForm, setShowForm] = useState(false)

  function toggleEstado(c: Cohorte) {
    actualizar({ id: c.id, payload: { activa: !c.activa } })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mt-4">
        <h3 className="font-headline-sm text-headline-sm text-on-surface">Cohortes</h3>
        <Button onClick={() => setShowForm(!showForm)} variant={showForm ? 'secondary' : 'primary'}>
          {showForm ? 'Cancelar' : '+ Nueva cohorte'}
        </Button>
      </div>
      {showForm && (
        <div className="rounded neo-latex-border bg-surface-container-lowest p-5">
          <CohorteForm onSuccess={() => setShowForm(false)} />
        </div>
      )}
      {isLoading && <div className="h-20 animate-pulse rounded neo-latex-border bg-surface-container" />}
      {!isLoading && data?.length === 0 && (
        <p className="py-6 text-center font-body-md text-on-surface-variant bg-surface-container-lowest rounded neo-latex-border">No hay cohortes registradas.</p>
      )}
      {!isLoading && data && data.length > 0 && (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                <th className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">Nombre</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Inicio</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Fin</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Estado</th>
                <th className="px-4 py-3 text-center font-label-caps text-label-caps uppercase text-on-surface-variant">Acción</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {data.map((c) => (
                <tr key={c.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md font-medium text-on-surface">{c.nombre}</td>
                  <td className="px-4 py-3 text-center font-mono-data text-[12px] text-on-surface-variant">{c.fecha_inicio ?? '—'}</td>
                  <td className="px-4 py-3 text-center font-mono-data text-[12px] text-on-surface-variant">{c.fecha_fin ?? '—'}</td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant={c.activa ? 'success' : 'neutral'}>
                      {c.activa ? 'Activa' : 'Inactiva'}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <Button onClick={() => toggleEstado(c)} variant="ghost" className="text-[12px] px-2 py-1 h-auto">
                      {c.activa ? 'Desactivar' : 'Activar'}
                    </Button>
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
