import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useFechasAcademicas, useCrearFechaAcademica } from '../hooks/useFechasAcademicasApi'
import type { TipoEvaluacion } from '../types'

const fechaSchema = z.object({
  materia_id: z.string().min(1, 'Requerido'),
  cohorte: z.string().min(1, 'Requerido'),
  tipo: z.enum(['parcial', 'tp', 'coloquio']),
  numero: z.number().int().min(1),
  fecha: z.string().min(1, 'Ingrese la fecha'),
  descripcion: z.string().optional(),
})

type FechaFormData = z.infer<typeof fechaSchema>

const TIPO_LABELS: Record<TipoEvaluacion, string> = {
  parcial: 'Parcial',
  tp: 'TP',
  coloquio: 'Coloquio',
}

export default function FechasAcademicasStep() {
  const [showForm, setShowForm] = useState(false)
  const { data, isLoading } = useFechasAcademicas()
  const crearMutation = useCrearFechaAcademica()
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FechaFormData>({
    resolver: zodResolver(fechaSchema),
    defaultValues: { tipo: 'parcial', numero: 1 },
  })

  const fechas = data?.data ?? []

  const onSubmit = (values: FechaFormData) => {
    crearMutation.mutate(values, {
      onSuccess: () => {
        setShowForm(false)
        reset()
      },
    })
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end">
        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          {showForm ? 'Cancelar' : '+ Agregar fecha'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="rounded-lg border border-gray-200 p-4">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">Materia ID</label>
              <input {...register('materia_id')} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
              {errors.materia_id && <p className="mt-1 text-xs text-red-600">{errors.materia_id.message}</p>}
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">Cohorte</label>
              <input {...register('cohorte')} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
              {errors.cohorte && <p className="mt-1 text-xs text-red-600">{errors.cohorte.message}</p>}
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">Tipo</label>
              <select {...register('tipo')} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm">
                <option value="parcial">Parcial</option>
                <option value="tp">TP</option>
                <option value="coloquio">Coloquio</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">Número</label>
              <input type="number" min={1} {...register('numero', { valueAsNumber: true })} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">Fecha</label>
              <input type="date" {...register('fecha')} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
              {errors.fecha && <p className="mt-1 text-xs text-red-600">{errors.fecha.message}</p>}
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-gray-700">Descripción (opcional)</label>
              <input {...register('descripcion')} className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm" />
            </div>
          </div>
          <div className="mt-3 flex gap-2">
            <button type="submit" disabled={crearMutation.isPending} className="rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
              {crearMutation.isPending ? 'Guardando...' : 'Guardar fecha'}
            </button>
          </div>
        </form>
      )}

      {isLoading ? (
        <p className="text-sm text-gray-500">Cargando fechas...</p>
      ) : fechas.length === 0 ? (
        <p className="text-sm text-gray-400">Sin fechas cargadas aún.</p>
      ) : (
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Materia', 'Cohorte', 'Tipo', 'N°', 'Fecha', 'Descripción'].map((h) => (
                <th key={h} className="px-4 py-2 text-left text-xs font-semibold uppercase text-gray-500">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {fechas.map((f) => (
              <tr key={f.id}>
                <td className="px-4 py-2 text-sm text-gray-900">{f.materia_nombre}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{f.cohorte}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{TIPO_LABELS[f.tipo]}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{f.numero}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{f.fecha}</td>
                <td className="px-4 py-2 text-sm text-gray-500">{f.descripcion ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}
