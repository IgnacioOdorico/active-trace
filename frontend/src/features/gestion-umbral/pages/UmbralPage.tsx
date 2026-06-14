import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMaterias } from '../../academico/hooks/useMaterias'
import { useUmbralApi } from '../hooks/useUmbralApi'
import { umbralSchema, type UmbralFormData } from '../schemas'

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
        materia_id,
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
    <div className="mx-auto max-w-2xl py-8">
      <h1 className="text-2xl font-bold text-gray-900">
        Umbral de Aprobación
      </h1>

      <div className="mt-6">
        <label
          htmlFor="materia"
          className="block text-sm font-medium text-gray-700"
        >
          Materia
        </label>
        <select
          id="materia"
          value={materiaId}
          onChange={(e) => handleMateriaChange(e.target.value)}
          className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
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
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-blue-600 border-t-transparent" />
          <p className="ml-3 text-sm text-gray-600">
            Cargando configuración actual...
          </p>
        </div>
      )}

      {materiaId && !current.isLoading && (
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="mt-8 space-y-6"
          noValidate
        >
          {saveSuccess && (
            <div className="rounded-md bg-green-50 p-4 text-sm font-medium text-green-800">
              {saveSuccess}
            </div>
          )}

          {update.isError && (
            <div className="rounded-md bg-red-50 p-4 text-sm font-medium text-red-800">
              {update.error instanceof Error
                ? update.error.message
                : 'Error al guardar la configuración'}
            </div>
          )}

          {current.data?.es_default && (
            <div className="rounded-md bg-yellow-50 p-4 text-sm text-yellow-800">
              Valor por defecto del sistema (60%). Configure el umbral para esta
              materia.
            </div>
          )}

          {!current.data?.es_default && (
            <div className="rounded-md bg-blue-50 p-4 text-sm text-blue-800">
              Umbral activo para <strong>{materiaNombre}</strong>:{' '}
              {current.data?.umbral_pct ?? 60}%
            </div>
          )}

          <div>
            <label
              htmlFor="umbral_pct"
              className="block text-sm font-medium text-gray-700"
            >
              Porcentaje de aprobación
            </label>
            <input
              id="umbral_pct"
              type="number"
              min={0}
              max={100}
              className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              {...register('umbral_pct', { valueAsNumber: true })}
            />
            {errors.umbral_pct && (
              <p className="mt-1 text-sm text-red-600">
                {errors.umbral_pct.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Valores textuales aprobatorios
            </label>
            <p className="mt-1 text-xs text-gray-500">
              Ej: Satisfactorio, Excelente, Aprobado
            </p>

            {valoresAprobatorios.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-2">
                {valoresAprobatorios.map((valor) => (
                  <span
                    key={valor}
                    className="inline-flex items-center rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800"
                  >
                    {valor}
                    <button
                      type="button"
                      onClick={() => handleEliminarValor(valor)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                      aria-label={`Eliminar ${valor}`}
                    >
                      &times;
                    </button>
                  </span>
                ))}
              </div>
            )}

            <div className="mt-2 flex gap-2">
              <input
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
                className="block flex-1 rounded-md border border-gray-300 px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <button
                type="button"
                onClick={handleAgregarValor}
                className="rounded-md bg-gray-100 px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
              >
                Agregar
              </button>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              type="submit"
              disabled={isSubmitting || update.isPending}
              className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {update.isPending ? 'Guardando...' : 'Guardar'}
            </button>
          </div>
        </form>
      )}
    </div>
  )
}
