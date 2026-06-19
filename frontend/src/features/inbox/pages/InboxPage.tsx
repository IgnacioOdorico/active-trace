import { useState, useEffect, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '../../auth/hooks/useAuth'
import { useHilos, useHilo, useResponderHilo } from '../hooks/useInboxApi'
import { responderSchema, type ResponderFormData } from '../schemas'
import type { HiloResumen } from '../types'

function formatFecha(dateStr: string | null): string {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return date.toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
  }
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return date.toLocaleDateString('es-AR', { weekday: 'long' })
  return date.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

function formatFechaCompleta(dateStr: string | null): string {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function InboxPage() {
  const { user } = useAuth()
  const [pagina, setPagina] = useState(1)
  const [hiloActivo, setHiloActivo] = useState<string | null>(null)
  const [hiloInfo, setHiloInfo] = useState<HiloResumen | null>(null)

  const mensajesEndRef = useRef<HTMLDivElement>(null)

  const { data: inboxData, isLoading: isLoadingHilos } = useHilos(pagina)
  const { data: hiloDetalle, isLoading: isLoadingHilo } = useHilo(hiloActivo)
  const { mutate: responder, isPending: isRespondiendo } = useResponderHilo()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ResponderFormData>({
    resolver: zodResolver(responderSchema),
  })

  const totalPaginas = inboxData ? Math.ceil(inboxData.total / inboxData.page_size) : 0

  useEffect(() => {
    mensajesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [hiloDetalle])

  const handleSeleccionarHilo = (hilo: HiloResumen) => {
    setHiloActivo(hilo.id)
    setHiloInfo(hilo)
  }

  const onSubmit = (data: ResponderFormData) => {
    if (!hiloActivo) return
    responder(
      { hiloId: hiloActivo, cuerpo: data.cuerpo },
      {
        onSuccess: () => {
          reset()
        },
      },
    )
  }

  const usuarioNombre = (id: string) => {
    if (id === user?.id) return 'Tú'
    return id.slice(0, 8)
  }

  const esEnvioPropio = (remitenteId: string) => remitenteId === user?.id

  return (
    <div className="flex flex-col gap-gutter h-[calc(100vh-10rem)]">
      <div className="flex justify-between items-end pb-4 border-b border-outline-variant">
        <div>
          <h2 className="font-headline-md text-headline-md text-primary">Mensajes</h2>
          <p className="font-body-md text-on-surface-variant mt-1">
            Bandeja de entrada y mensajería interna.
          </p>
        </div>
      </div>

      <div className="flex-1 bg-surface-container-lowest border border-outline-variant overflow-hidden grid grid-cols-12">
        <div className="col-span-5 border-r border-outline-variant flex flex-col">
          <div className="p-4 border-b border-outline-variant flex items-center justify-between">
            <h3 className="font-label-caps text-label-caps text-primary font-bold uppercase">
              Bandeja de Entrada
            </h3>
            <span className="font-mono-data text-mono-data text-on-surface-variant">
              {inboxData?.total ?? 0}
            </span>
          </div>

          <div className="flex-1 overflow-y-auto">
            {isLoadingHilos && (
              <div className="flex items-center justify-center py-12">
                <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
              </div>
            )}

            {inboxData?.items.length === 0 && (
              <div className="flex items-center justify-center py-12">
                <p className="font-body-md text-on-surface-variant">No hay mensajes</p>
              </div>
            )}

            {inboxData?.items.map((hilo) => (
              <button
                key={hilo.id}
                type="button"
                onClick={() => handleSeleccionarHilo(hilo)}
                className={`w-full text-left p-4 cursor-pointer border-b border-outline-variant transition-colors ${
                  hiloActivo === hilo.id
                    ? 'bg-secondary-container/30 border-l-2 border-primary'
                    : 'hover:bg-surface-container'
                }`}
              >
                <div className="flex justify-between mb-1">
                  <span
                    className={`font-label-caps text-[11px] font-bold ${
                      !hilo.leido
                        ? 'text-primary'
                        : 'text-on-surface-variant'
                    }`}
                  >
                    {usuarioNombre(hilo.remitente_id)}
                  </span>
                  <span className="font-mono-data text-[10px] text-on-surface-variant">
                    {formatFecha(hilo.created_at)}
                  </span>
                </div>
                <h4
                  className={`font-body-md mb-1 truncate ${
                    !hilo.leido ? 'font-semibold text-on-surface' : 'text-on-surface'
                  }`}
                >
                  {hilo.asunto}
                </h4>
                <p className="font-body-md text-[13px] text-on-surface-variant line-clamp-2">
                  {hilo.ultimo_mensaje}
                </p>
              </button>
            ))}
          </div>

          {totalPaginas > 1 && (
            <div className="flex items-center justify-between p-4 border-t border-outline-variant">
              <button
                type="button"
                onClick={() => setPagina((p) => Math.max(1, p - 1))}
                disabled={pagina <= 1}
                className="font-label-caps text-label-caps text-on-surface-variant hover:text-primary transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Anterior
              </button>
              <span className="font-mono-data text-mono-data text-on-surface-variant">
                {pagina} / {totalPaginas}
              </span>
              <button
                type="button"
                onClick={() => setPagina((p) => p + 1)}
                disabled={pagina >= totalPaginas}
                className="font-label-caps text-label-caps text-on-surface-variant hover:text-primary transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
              >
                Siguiente
              </button>
            </div>
          )}
        </div>

        <div className="col-span-7 flex flex-col">
          {!hiloActivo ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <span className="material-symbols-outlined text-4xl text-on-surface-variant mb-2">
                  mail_outline
                </span>
                <p className="font-body-md text-on-surface-variant">
                  Seleccioná un mensaje para ver la conversación
                </p>
              </div>
            </div>
          ) : isLoadingHilo ? (
            <div className="flex-1 flex items-center justify-center">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
            </div>
          ) : hiloDetalle ? (
            <>
              <div className="p-4 border-b border-outline-variant flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-surface-container-high border border-outline-variant flex items-center justify-center">
                  <span className="material-symbols-outlined text-[16px] text-on-surface-variant">
                    person
                  </span>
                </div>
                <div>
                  <h3 className="font-body-md font-bold text-primary">
                    {usuarioNombre(
                      esEnvioPropio(hiloDetalle.remitente_id)
                        ? hiloDetalle.destinatario_id
                        : hiloDetalle.remitente_id,
                    )}
                  </h3>
                  <p className="font-label-caps text-[10px] text-on-surface-variant uppercase">
                    {hiloDetalle.asunto}
                  </p>
                </div>
              </div>

              <div className="flex-1 p-6 overflow-y-auto flex flex-col gap-6 bg-surface-container-low/20">
                <div
                  className={`flex gap-3 max-w-[85%] ${
                    esEnvioPropio(hiloDetalle.remitente_id) ? 'self-end flex-row-reverse' : ''
                  }`}
                >
                  <div className="flex flex-col">
                    <div
                      className={`p-3 border border-outline-variant ${
                        esEnvioPropio(hiloDetalle.remitente_id)
                          ? 'bg-primary text-on-primary'
                          : 'bg-white'
                      }`}
                    >
                      <p
                        className={`font-body-md ${
                          esEnvioPropio(hiloDetalle.remitente_id)
                            ? 'text-on-primary'
                            : 'text-on-surface'
                        }`}
                      >
                        {hiloDetalle.cuerpo}
                      </p>
                    </div>
                    <span
                      className={`font-mono-data text-[10px] text-on-surface-variant mt-1 ${
                        esEnvioPropio(hiloDetalle.remitente_id) ? 'self-end' : 'self-start'
                      }`}
                    >
                      {formatFechaCompleta(hiloDetalle.created_at)}
                    </span>
                  </div>
                </div>

                {hiloDetalle.respuestas.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex gap-3 max-w-[85%] ${
                      esEnvioPropio(msg.remitente_id) ? 'self-end flex-row-reverse' : ''
                    }`}
                  >
                    <div className="flex flex-col">
                      <div
                        className={`p-3 border border-outline-variant ${
                          esEnvioPropio(msg.remitente_id)
                            ? 'bg-primary text-on-primary'
                            : 'bg-white'
                        }`}
                      >
                        <p
                          className={`font-body-md ${
                            esEnvioPropio(msg.remitente_id)
                              ? 'text-on-primary'
                              : 'text-on-surface'
                          }`}
                        >
                          {msg.cuerpo}
                        </p>
                      </div>
                      <span
                        className={`font-mono-data text-[10px] text-on-surface-variant mt-1 ${
                          esEnvioPropio(msg.remitente_id) ? 'self-end' : 'self-start'
                        }`}
                      >
                        {formatFechaCompleta(msg.created_at)}
                      </span>
                    </div>
                  </div>
                ))}
                <div ref={mensajesEndRef} />
              </div>

              <form
                onSubmit={handleSubmit(onSubmit)}
                className="p-4 bg-white border-t border-outline-variant"
              >
                <div className="flex items-end gap-2 border border-outline-variant p-2 focus-within:border-primary transition-colors">
                  <textarea
                    {...register('cuerpo')}
                    placeholder="Escribí tu mensaje..."
                    rows={1}
                    className="flex-grow bg-transparent border-0 focus:ring-0 font-body-md text-body-md resize-none py-1 outline-none"
                    onInput={(e) => {
                      const el = e.currentTarget
                      el.style.height = 'auto'
                      el.style.height = `${el.scrollHeight}px`
                    }}
                  />
                  <button
                    type="submit"
                    disabled={isRespondiendo}
                    className="bg-primary text-on-primary p-2 hover:opacity-90 transition-opacity flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="material-symbols-outlined text-[18px]">send</span>
                  </button>
                </div>
                {errors.cuerpo && (
                  <p className="font-mono-data text-[11px] text-error mt-1">{errors.cuerpo.message}</p>
                )}
              </form>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <p className="font-body-md text-on-surface-variant">Error al cargar el mensaje.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
