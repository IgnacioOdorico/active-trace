import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { usePerfil, useActualizarPerfil } from '../hooks/usePerfilApi'
import { perfilSchema, type PerfilFormData } from '../schemas'

const regionales = [
  'Regional Centro - Buenos Aires',
  'Regional Cuyo - Mendoza',
  'Regional Norte - Salta',
  'Regional Patagonia - Neuquén',
  'Regional Litoral - Santa Fe',
  'Regional NEA - Corrientes',
  'Regional NOA - Tucumán',
  'Regional Oeste - San Juan',
]

export default function PerfilPage() {
  const { data: perfil, isLoading, isError } = usePerfil()
  const { mutate: actualizar, isPending } = useActualizarPerfil()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<PerfilFormData>({
    resolver: zodResolver(perfilSchema),
  })

  useEffect(() => {
    if (perfil) {
      reset({
        nombre: perfil.nombre,
        apellidos: perfil.apellidos,
        dni: perfil.dni,
        cbu: perfil.cbu,
        alias_cbu: perfil.alias_cbu,
        banco: perfil.banco,
        regional: perfil.regional,
        email: perfil.email,
        legajo_profesional: perfil.legajo_profesional,
        facturador: perfil.facturador,
      })
    }
  }, [perfil, reset])

  const onSubmit = (data: PerfilFormData) => {
    actualizar(data)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (isError || !perfil) {
    return (
      <div className="bg-surface-container-lowest border border-outline-variant p-6">
        <p className="font-body-md text-error">Error al cargar el perfil.</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-gutter">
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant">
        <div>
          <h2 className="font-headline-md text-headline-md text-primary">Perfil</h2>
          <p className="font-body-md text-on-surface-variant mt-1">
            Datos personales y configuración de cuenta.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-bento-gap">
        <div className="lg:col-span-3 flex flex-col gap-bento-gap">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-surface-container-lowest border border-outline-variant p-6">
              <div className="flex items-center justify-between mb-6 border-b border-outline-variant pb-2">
                <h3 className="font-label-caps text-label-caps text-primary font-bold uppercase tracking-widest">
                  Información de Perfil
                </h3>
                <span className="material-symbols-outlined text-primary">edit_note</span>
              </div>

              <div className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      CUIL (Solo lectura)
                    </label>
                    <div className="bg-surface-container-low px-3 py-2 font-mono-data text-mono-data text-on-surface-variant border-b border-outline-variant">
                      {perfil.cuil ?? '—'}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      Nombre
                    </label>
                    <input
                      {...register('nombre')}
                      className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-body-md text-body-md px-1 py-1 outline-none transition-colors"
                    />
                    {errors.nombre && (
                      <p className="font-mono-data text-[11px] text-error mt-1">{errors.nombre.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      Apellidos
                    </label>
                    <input
                      {...register('apellidos')}
                      className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-body-md text-body-md px-1 py-1 outline-none transition-colors"
                    />
                    {errors.apellidos && (
                      <p className="font-mono-data text-[11px] text-error mt-1">{errors.apellidos.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      Email
                    </label>
                    <input
                      {...register('email')}
                      type="email"
                      className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-body-md text-body-md px-1 py-1 outline-none transition-colors"
                    />
                    {errors.email && (
                      <p className="font-mono-data text-[11px] text-error mt-1">{errors.email.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      DNI
                    </label>
                    <input
                      {...register('dni')}
                      className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-body-md text-body-md px-1 py-1 outline-none transition-colors"
                    />
                    {errors.dni && (
                      <p className="font-mono-data text-[11px] text-error mt-1">{errors.dni.message}</p>
                    )}
                  </div>
                </div>

                <div className="pt-4 border-t border-outline-variant">
                  <h4 className="font-label-caps text-label-caps text-primary uppercase tracking-widest mb-4">
                    Datos Bancarios
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                        CBU / CVU
                      </label>
                      <input
                        {...register('cbu')}
                        className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-mono-data text-mono-data px-1 py-1 outline-none transition-colors"
                      />
                      {errors.cbu && (
                        <p className="font-mono-data text-[11px] text-error mt-1">{errors.cbu.message}</p>
                      )}
                    </div>
                    <div>
                      <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                        Alias
                      </label>
                      <input
                        {...register('alias_cbu')}
                        className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-mono-data text-mono-data px-1 py-1 outline-none transition-colors"
                      />
                      {errors.alias_cbu && (
                        <p className="font-mono-data text-[11px] text-error mt-1">{errors.alias_cbu.message}</p>
                      )}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      Banco
                    </label>
                    <input
                      {...register('banco')}
                      className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-body-md text-body-md px-1 py-1 outline-none transition-colors"
                    />
                    {errors.banco && (
                      <p className="font-mono-data text-[11px] text-error mt-1">{errors.banco.message}</p>
                    )}
                  </div>
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      Regional / Dependencia
                    </label>
                    <select
                      {...register('regional')}
                      className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-body-md text-body-md px-1 py-1 outline-none transition-colors"
                    >
                      <option value="">Seleccionar regional</option>
                      {regionales.map((r) => (
                        <option key={r} value={r}>
                          {r}
                        </option>
                      ))}
                    </select>
                    {errors.regional && (
                      <p className="font-mono-data text-[11px] text-error mt-1">{errors.regional.message}</p>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="font-label-caps text-[10px] uppercase text-on-surface-variant mb-1 block">
                      Legajo Profesional
                    </label>
                    <input
                      {...register('legajo_profesional')}
                      className="w-full bg-transparent border-0 border-b border-outline focus:ring-0 focus:border-primary font-body-md text-body-md px-1 py-1 outline-none transition-colors"
                    />
                  </div>
                  <div className="flex items-end pb-2">
                    <label className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        {...register('facturador')}
                        className="w-4 h-4 rounded border-outline text-primary focus:ring-primary"
                      />
                      <span className="font-label-caps text-label-caps text-on-surface-variant">
                        Facturador
                      </span>
                    </label>
                  </div>
                </div>

                <div className="flex justify-end gap-3 pt-4 border-t border-outline-variant">
                  <button
                    type="button"
                    onClick={() => reset()}
                    className="font-label-caps text-label-caps text-on-surface-variant px-4 py-2 hover:bg-surface-container-high transition-colors"
                  >
                    Descartar
                  </button>
                  <button
                    type="submit"
                    disabled={!isDirty || isPending}
                    className="font-label-caps text-label-caps bg-primary text-on-primary px-6 py-2 hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isPending ? 'Guardando...' : 'Guardar Cambios'}
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>

        <div className="lg:col-span-2 flex flex-col gap-bento-gap">
          <div className="bg-primary-container text-on-primary-fixed-variant p-6 border border-outline-variant">
            <h4 className="font-label-caps text-label-caps mb-4 border-b border-on-primary/20 pb-2">
              Resumen de Cuenta
            </h4>
            <div className="space-y-4">
              <div>
                <p className="font-label-caps text-[10px] opacity-70 uppercase">Estado</p>
                <p className="font-body-md font-medium">{perfil.estado}</p>
              </div>
              <div>
                <p className="font-label-caps text-[10px] opacity-70 uppercase">Legajo</p>
                <p className="font-mono-data text-mono-data">{perfil.legajo ?? '—'}</p>
              </div>
              <div>
                <p className="font-label-caps text-[10px] opacity-70 uppercase">Miembro desde</p>
                <p className="font-body-md">
                  {perfil.created_at
                    ? new Date(perfil.created_at).toLocaleDateString('es-AR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : '—'}
                </p>
              </div>
              <div>
                <p className="font-label-caps text-[10px] opacity-70 uppercase">Facturador</p>
                <p className="font-body-md">{perfil.facturador ? 'Sí' : 'No'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
