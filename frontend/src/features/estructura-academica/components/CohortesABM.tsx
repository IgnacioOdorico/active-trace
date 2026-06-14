import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { cohorteSchema, type CohorteFormValues } from '../schemas'
import { useCarreras, useCohortes, useCrearCohorte, useActualizarCohorte } from '../hooks/useEstructuraApi'
import type { Cohorte } from '../types'

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
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Nombre *</label>
          <input {...register('nombre')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" placeholder="Ej: 2024-1" />
          {errors.nombre && <p className="text-xs text-red-600">{errors.nombre.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Carrera *</label>
          <select {...register('carrera_id')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none">
            <option value="">Seleccioná</option>
            {carreras?.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
          </select>
          {errors.carrera_id && <p className="text-xs text-red-600">{errors.carrera_id.message}</p>}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Fecha inicio</label>
          <input type="date" {...register('fecha_inicio')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Fecha fin</label>
          <input type="date" {...register('fecha_fin')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
          {errors.fecha_fin && <p className="text-xs text-red-600">{errors.fecha_fin.message}</p>}
        </div>
      </div>
      {errors.root && <p className="rounded bg-red-50 p-2 text-xs text-red-700">{errors.root.message}</p>}
      <div className="flex justify-end">
        <button type="submit" disabled={isPending} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {isPending ? 'Guardando...' : 'Crear cohorte'}
        </button>
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
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700">Cohortes</h3>
        <button onClick={() => setShowForm(!showForm)} className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700">
          {showForm ? 'Cancelar' : '+ Nueva cohorte'}
        </button>
      </div>
      {showForm && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <CohorteForm onSuccess={() => setShowForm(false)} />
        </div>
      )}
      {isLoading && <div className="h-20 animate-pulse rounded bg-gray-200" />}
      {!isLoading && data?.length === 0 && (
        <p className="py-4 text-center text-sm text-gray-500">No hay cohortes registradas.</p>
      )}
      {!isLoading && data && data.length > 0 && (
        <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Nombre</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Inicio</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Fin</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Acción</th>
            </tr>
          </thead>
          <tbody>
            {data.map((c) => (
              <tr key={c.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium text-gray-900">{c.nombre}</td>
                <td className="px-4 py-2 text-center text-sm text-gray-600">{c.fecha_inicio ?? '—'}</td>
                <td className="px-4 py-2 text-center text-sm text-gray-600">{c.fecha_fin ?? '—'}</td>
                <td className="px-4 py-2 text-center">
                  <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${c.activa ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
                    {c.activa ? 'Activa' : 'Inactiva'}
                  </span>
                </td>
                <td className="px-4 py-2 text-center">
                  <button onClick={() => toggleEstado(c)} className="rounded px-2 py-1 text-xs text-blue-600 hover:bg-blue-50">
                    {c.activa ? 'Desactivar' : 'Activar'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
