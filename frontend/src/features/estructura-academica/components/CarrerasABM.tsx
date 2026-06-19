import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { carreraSchema, type CarreraFormValues } from '../schemas'
import { useCarreras, useCrearCarrera, useActualizarCarrera } from '../hooks/useEstructuraApi'
import type { Carrera } from '../types'

function CarreraForm({ onSuccess }: { onSuccess: () => void }) {
  const { mutate, isPending } = useCrearCarrera()
  const { register, handleSubmit, setError, formState: { errors } } = useForm<CarreraFormValues>({
    resolver: zodResolver(carreraSchema),
  })

  function onSubmit(values: CarreraFormValues) {
    mutate(values, {
      onSuccess,
      onError: (err: unknown) => {
        const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? ''
        setError('root', { message: `Error: ${detail}` })
      },
    })
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
      <div className="grid grid-cols-2 gap-3">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Código *</label>
          <input {...register('codigo')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" placeholder="Ej: SIS" />
          {errors.codigo && <p className="text-xs text-red-600">{errors.codigo.message}</p>}
        </div>
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-gray-700">Nombre *</label>
          <input {...register('nombre')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" placeholder="Ej: Sistemas" />
          {errors.nombre && <p className="text-xs text-red-600">{errors.nombre.message}</p>}
        </div>
      </div>
      <div className="flex flex-col gap-1">
        <label className="text-sm font-medium text-gray-700">Descripción</label>
        <input {...register('descripcion')} className="rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none" />
      </div>
      {errors.root && <p className="rounded bg-red-50 p-2 text-xs text-red-700">{errors.root.message}</p>}
      <div className="flex justify-end">
        <button type="submit" disabled={isPending} className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {isPending ? 'Guardando...' : 'Crear carrera'}
        </button>
      </div>
    </form>
  )
}

export default function CarrerasABM() {
  const { data, isLoading } = useCarreras()
  const { mutate: actualizar } = useActualizarCarrera()
  const [showForm, setShowForm] = useState(false)

  function toggleEstado(carrera: Carrera) {
    actualizar({ id: carrera.id, payload: { activa: !carrera.activa } })
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-700">Carreras</h3>
        <button onClick={() => setShowForm(!showForm)} className="rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700">
          {showForm ? 'Cancelar' : '+ Nueva carrera'}
        </button>
      </div>
      {showForm && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-4">
          <CarreraForm onSuccess={() => setShowForm(false)} />
        </div>
      )}
      {isLoading && <div className="h-20 animate-pulse rounded bg-gray-200" />}
      {!isLoading && data?.length === 0 && (
        <p className="py-4 text-center text-sm text-gray-500">No hay carreras registradas.</p>
      )}
      {!isLoading && data && data.length > 0 && (
        <table className="w-full overflow-hidden rounded-lg border border-gray-200 bg-white">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Código</th>
              <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Nombre</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Estado</th>
              <th className="px-4 py-2 text-center text-xs font-medium text-gray-500">Acción</th>
            </tr>
          </thead>
          <tbody>
            {data.map((c) => (
              <tr key={c.id} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="px-4 py-2 text-sm font-medium text-gray-900">{c.codigo}</td>
                <td className="px-4 py-2 text-sm text-gray-700">{c.nombre}</td>
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
