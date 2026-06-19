import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useFechasAcademicas, useCrearFechaAcademica } from '../hooks/useFechasAcademicasApi'
import type { TipoEvaluacion } from '../types'
import { Input } from '../../../shared/components/ui/Input'
import { Button } from '../../../shared/components/ui/Button'

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
        <Button
          onClick={() => setShowForm(!showForm)}
          variant={showForm ? 'secondary' : 'primary'}
        >
          {showForm ? 'Cancelar' : '+ Agregar fecha'}
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit(onSubmit)} className="rounded neo-latex-border bg-surface-container-lowest p-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Materia ID</label>
              <Input {...register('materia_id')} className="w-full" />
              {errors.materia_id && <p className="font-body-md text-[12px] text-error">{errors.materia_id.message}</p>}
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Cohorte</label>
              <Input {...register('cohorte')} className="w-full" />
              {errors.cohorte && <p className="font-body-md text-[12px] text-error">{errors.cohorte.message}</p>}
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Tipo</label>
              <select {...register('tipo')} className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary">
                <option value="parcial">Parcial</option>
                <option value="tp">TP</option>
                <option value="coloquio">Coloquio</option>
              </select>
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Número</label>
              <Input type="number" min={1} {...register('numero', { valueAsNumber: true })} className="w-full" />
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Fecha</label>
              <Input type="date" {...register('fecha')} className="w-full" />
              {errors.fecha && <p className="font-body-md text-[12px] text-error">{errors.fecha.message}</p>}
            </div>
            <div className="flex flex-col gap-1">
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">Descripción (opcional)</label>
              <Input {...register('descripcion')} className="w-full" />
            </div>
          </div>
          <div className="mt-4 flex gap-2">
            <Button type="submit" disabled={crearMutation.isPending} variant="primary">
              {crearMutation.isPending ? 'Guardando...' : 'Guardar fecha'}
            </Button>
          </div>
        </form>
      )}

      {isLoading ? (
        <p className="font-body-md text-on-surface-variant">Cargando fechas...</p>
      ) : fechas.length === 0 ? (
        <p className="font-body-md text-on-surface-variant">Sin fechas cargadas aún.</p>
      ) : (
        <div className="overflow-x-auto rounded neo-latex-border bg-surface-container-lowest">
          <table className="min-w-full divide-y divide-outline-variant">
            <thead className="bg-surface">
              <tr>
                {['Materia', 'Cohorte', 'Tipo', 'N°', 'Fecha', 'Descripción'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-label-caps text-label-caps uppercase text-on-surface-variant">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant bg-surface-container-lowest">
              {fechas.map((f) => (
                <tr key={f.id} className="hover:bg-surface-container transition-colors">
                  <td className="px-4 py-3 font-body-md text-body-md text-on-surface">{f.materia_nombre}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{f.cohorte}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{TIPO_LABELS[f.tipo]}</td>
                  <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface">{f.numero}</td>
                  <td className="px-4 py-3 font-mono-data text-mono-data text-on-surface">{f.fecha}</td>
                  <td className="px-4 py-3 font-body-md text-[12px] text-on-surface-variant">{f.descripcion ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
