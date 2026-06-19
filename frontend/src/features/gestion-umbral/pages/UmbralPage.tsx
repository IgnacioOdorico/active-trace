import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useUmbralApi } from '../hooks/useUmbralApi'
import { umbralSchema, type UmbralFormData } from '../schemas'
import { BentoCard } from '../../../shared/components/ui/BentoCard'
import { Button } from '../../../shared/components/ui/Button'
import { Input } from '../../../shared/components/ui/Input'
import { Badge } from '../../../shared/components/ui/Badge'

export default function UmbralPage() {
  const { data: materias, isLoading: materiasLoading } = useMaterias()
  const [materiaId, setMateriaId] = useState('')
  const { current, update } = useUmbralApi(materiaId || null)
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null)
  const [valoresAprobatorios, setValoresAprobatorios] = useState<string[]>([])
  const [nuevoValor, setNuevoValor] = useState('')

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<UmbralFormData>({
    resolver: zodResolver(umbralSchema),
    defaultValues: {
      materia_id: '',
      umbral_pct: 60,
      valores_aprobatorios: [],
    },
  })

  function handleMateriaChange(value: string) {
    setMateriaId(value)
    setSaveSuccess(null)
    setValoresAprobatorios([])
    reset({
      materia_id: value,
      umbral_pct: 60,
      valores_aprobatorios: [],
    })
  }

  useEffect(() => {
    if (current.data && !current.isFetching) {
      setValoresAprobatorios(current.data.valores_aprobatorios)
      reset({
        materia_id: materiaId,
        umbral_pct: current.data.umbral_pct,
        valores_aprobatorios: current.data.valores_aprobatorios,
      })
    }
  }, [current.data, current.isFetching, materiaId, reset])

  async function onSubmit(data: UmbralFormData) {
    setSaveSuccess(null)
    try {
      const result = await update.mutateAsync({
        materia_id: data.materia_id,
        umbral_pct: data.umbral_pct,
        valores_aprobatorios: valoresAprobatorios,
      })
      setSaveSuccess(
        result.mensaje ||
          `Umbral actualizado. Se recalcularon ${result.recalculo_count ?? 0} calificaciones.`,
      )
    } catch {
      // error handled by useMutation
    }
  }

  function handleAgregarValor() {
    const trimmed = nuevoValor.trim()
    if (trimmed && !valoresAprobatorios.includes(trimmed)) {
      setValoresAprobatorios([...valoresAprobatorios, trimmed])
      setNuevoValor('')
    }
  }

  function handleEliminarValor(valor: string) {
    setValoresAprobatorios(
      valoresAprobatorios.filter((v) => v !== valor),
    )
  }

  const materiaNombre = materias?.find((m) => m.id === materiaId)?.nombre

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="font-headline-md text-headline-md text-on-surface">
          Umbral de Aprobación
        </h1>
      </div>

      <BentoCard>
        <div className="flex flex-col gap-1 mb-6">
          <label
            htmlFor="materia"
            className="font-label-caps text-label-caps text-on-surface-variant uppercase"
          >
            Materia
          </label>
          <select
            id="materia"
            value={materiaId}
            onChange={(e) => handleMateriaChange(e.target.value)}
            className="w-full neo-latex-border rounded bg-surface-container-lowest px-3 py-2 font-body-md text-on-surface focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
          >
            <option value="">Seleccione una materia</option>
            {materiasLoading && (
              <option value="" disabled>
                Cargando materias...
              </option>
            )}
            {materias?.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nombre}
                {m.comision ? ` - ${m.comision}` : ''}
              </option>
            ))}
          </select>
        </div>

        {current.isLoading && materiaId && (
          <div className="mt-8 flex items-center justify-center py-8">
            <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            <p className="ml-3 font-body-md text-on-surface-variant">
              Cargando configuración actual...
            </p>
          </div>
        )}

        {materiaId && !current.isLoading && (
          <form
            onSubmit={handleSubmit(onSubmit)}
            className="space-y-6"
            noValidate
          >
            {saveSuccess && (
              <div className="rounded neo-latex-border bg-[#d4edda] p-4 font-body-md text-[#155724]">
                {saveSuccess}
              </div>
            )}

            {update.isError && (
              <div className="rounded neo-latex-border bg-error-container p-4 font-body-md text-on-error-container">
                {update.error instanceof Error
                  ? update.error.message
                  : 'Error al guardar la configuración'}
              </div>
            )}

            {current.data?.es_default && (
              <div className="rounded neo-latex-border bg-surface-container p-4 font-body-md text-on-surface-variant">
                Valor por defecto del sistema (60%). Configure el umbral para esta
                materia.
              </div>
            )}

            {!current.data?.es_default && (
              <div className="rounded neo-latex-border bg-surface-container p-4 font-body-md text-on-surface">
                Umbral activo para <strong>{materiaNombre}</strong>:{' '}
                {current.data?.umbral_pct ?? 60}%
              </div>
            )}

            <div>
              <Input
                label="Porcentaje de aprobación"
                id="umbral_pct"
                type="number"
                min={0}
                max={100}
                error={errors.umbral_pct?.message}
                {...register('umbral_pct', { valueAsNumber: true })}
              />
            </div>

            <div>
              <label className="font-label-caps text-label-caps text-on-surface-variant uppercase">
                Valores textuales aprobatorios
              </label>
              <p className="mt-1 font-body-md text-[12px] text-on-surface-variant">
                Ej: Satisfactorio, Excelente, Aprobado
              </p>

              {valoresAprobatorios.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {valoresAprobatorios.map((valor) => (
                    <Badge key={valor} variant="info" className="flex items-center gap-1">
                      {valor}
                      <button
                        type="button"
                        onClick={() => handleEliminarValor(valor)}
                        className="material-symbols-outlined text-[14px] hover:text-on-surface"
                        aria-label={`Eliminar ${valor}`}
                      >
                        close
                      </button>
                    </Badge>
                  ))}
                </div>
              )}

              <div className="mt-3 flex gap-2">
                <Input
                  type="text"
                  value={nuevoValor}
                  onChange={(e) => setNuevoValor(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault()
                      handleAgregarValor()
                    }
                  }}
                  placeholder="Agregar valor..."
                  className="flex-1"
                />
                <Button
                  type="button"
                  onClick={handleAgregarValor}
                  variant="secondary"
                >
                  Agregar
                </Button>
              </div>
            </div>

            <div className="flex gap-3 pt-4 border-t border-outline-variant">
              <Button
                type="submit"
                disabled={isSubmitting || update.isPending}
                variant="primary"
              >
                {update.isPending ? 'Guardando...' : 'Guardar'}
              </Button>
            </div>
          </form>
        )}
      </BentoCard>
    </div>
  )
}
