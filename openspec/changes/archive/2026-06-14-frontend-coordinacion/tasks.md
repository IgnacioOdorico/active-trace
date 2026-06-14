## 1. Andamiaje y navegación (base compartida)

- [x] 1.1 Crear las carpetas de feature `frontend/src/features/{equipos,avisos,tareas,encuentros-admin,coloquios,setup-cuatrimestre}/` con subcarpetas `components/`, `hooks/`, `pages/` y archivos `types.ts`/`index.ts` siguiendo el patrón de C-22.
- [x] 1.2 Agregar la sección de menú "Coordinación" en `frontend/src/features/shell/components/Layout.tsx` con ítems protegidos por `equipos:asignar`, `avisos:publicar`, `tareas:gestionar`, `encuentros:gestionar`, `monitores:ver` (reusando el filtro de permisos existente).
- [x] 1.3 Registrar las rutas protegidas de las nuevas páginas en `frontend/src/pages/Router.tsx` bajo el `Layout` autenticado.
- [x] 1.4 Verificar que `apiClient` (`shared/services/httpClient.ts`) cubre el manejo de 401/403 y refresh para los nuevos endpoints; no modificarlo salvo gap real.

## 2. Equipos docentes (Épica 4)

- [x] 2.1 Definir `features/equipos/types.ts` con las interfaces de respuesta de `/api/equipos/*` (mis-equipos, asignacion-masiva, clonar, vigencia, vigencia-masiva) derivadas de los `*Response` del router.
- [x] 2.2 Crear `features/equipos/hooks/useEquiposApi.ts` con queries (`useMisEquipos`) y mutations (`useAsignacionMasiva`, `useClonarEquipo`, `useModificarVigencia`, `useModificarVigenciaMasiva`) sobre `apiClient`, con `invalidateQueries`.
- [x] 2.3 Crear `features/equipos/schemas.ts` (Zod) para asignación masiva, clonado y vigencia (validando `desde < hasta` y scope requerido).
- [x] 2.4 Implementar el componente de listado "Mis Equipos" con filtros (estado de vigencia, materia, rol) y estado vacío.
- [x] 2.5 Implementar el componente/formulario de asignación masiva (selección múltiple de docentes + materia × carrera × cohorte × rol + vigencia), con manejo de error 422.
- [x] 2.6 Implementar el componente/formulario de clonado de equipo (origen → cohorte destino) mostrando ids creados y el caso `ids_creados: []`.
- [x] 2.7 Implementar la modificación de vigencia individual y en bloque (mostrar filas afectadas).
- [x] 2.8 Implementar la acción de exportar equipo (`GET /api/equipos/{id}/exportar`) manejando la descarga binaria.
- [x] 2.9 Ensamblar `features/equipos/pages/EquiposPage.tsx` (< 200 LOC por componente) integrando listado y acciones.

## 3. Avisos (F3.5, FL-09)

- [x] 3.1 Definir `features/avisos/types.ts` con las interfaces de `/api/avisos/*` (Aviso, lista de gestión con contadores de ack).
- [x] 3.2 Crear `features/avisos/hooks/useAvisosApi.ts` con `useAvisosGestion`, `useCrearAviso`, `useEditarAviso`, `useEliminarAviso`, `useAckAviso`.
- [x] 3.3 Crear `features/avisos/schemas.ts` (Zod) con validación de scope condicional (materia/cohorte/rol según alcance) y de ventana de vigencia (inicio < fin).
- [x] 3.4 Implementar el formulario de ABM de aviso (alcance, contexto, roles, severidad, título/cuerpo, vigencia, orden, activo, requiere_ack).
- [x] 3.5 Implementar la vista de gestión con listado ordenado por prioridad y contadores de acknowledgment.
- [x] 3.6 Implementar la confirmación de lectura (`POST /api/avisos/{id}/ack`) y el ocultamiento del aviso tras el ack.
- [x] 3.7 Ensamblar `features/avisos/pages/AvisosPage.tsx`.

## 4. Tareas internas (Épica 8, FL-05)

- [x] 4.1 Definir `features/tareas/types.ts` con Tarea, ComentarioTarea, filtros de administración y estados (Pendiente/En progreso/Resuelta/Cancelada).
- [x] 4.2 Crear `features/tareas/hooks/useTareasApi.ts` con `useMisTareas`, `useTareasAdmin`, `useCrearTarea`, `useCambiarEstadoTarea`, `useComentarios`, `useAgregarComentario`.
- [x] 4.3 Crear `features/tareas/schemas.ts` (Zod) para alta/delegación de tarea.
- [x] 4.4 Implementar la vista "Mis Tareas".
- [x] 4.5 Implementar la administración global con filtros (asignado, asignador, materia, estado, búsqueda libre).
- [x] 4.6 Implementar el alta/delegación de tarea con trazabilidad asignador/asignado.
- [x] 4.7 Implementar el cambio de estado (workflow) y el hilo de comentarios.
- [x] 4.8 Ensamblar `features/tareas/pages/TareasPage.tsx`.

## 5. Monitores transversales (F2.7, F2.9)

- [x] 5.1 Reutilizar `features/monitor-seguimiento` (hooks `useMonitorGeneral`/`useMonitorSeguimiento`) para las vistas de coordinación; agregar wrapper de página/entrada de menú con permiso de coordinación si hace falta.
- [x] 5.2 Verificar/asegurar el filtro de rango de fechas (`fecha_desde`/`fecha_hasta`) en el monitor de seguimiento coordinación/admin (F2.9).
- [x] 5.3 Asegurar el filtrado del monitor general (materia, regional, comisión, búsqueda, estado, clasificación) y la acción "Limpiar".

## 6. Encuentros (vista admin) y guardias (F6.5, FL-06)

- [x] 6.1 Definir `features/encuentros-admin/types.ts` con InstanciaEncuentro y Guardia (de `/api/encuentros/instancias` y `/api/guardias`).
- [x] 6.2 Crear `features/encuentros-admin/hooks/useEncuentrosAdminApi.ts` con `useEncuentrosInstancias` (listado global), `useGuardias`, `useRegistrarGuardia`, `useEditarGuardia`, y export de guardias.
- [x] 6.3 Implementar la vista transversal de encuentros con filtro por materia y estado realizado/pendiente.
- [x] 6.4 Implementar el registro/consulta global de guardias con filtros y la acción de exportar (`GET /api/guardias/exportar`).
- [x] 6.5 Ensamblar `features/encuentros-admin/pages/EncuentrosAdminPage.tsx`.

## 7. Coloquios (Épica 7)

- [x] 7.1 Definir `features/coloquios/types.ts` con Convocatoria, métricas y listado (de `/api/coloquios/*`, tipando los `response_model=dict` según el service).
- [x] 7.2 Crear `features/coloquios/hooks/useColoquiosApi.ts` con `useMetricas`, `useConvocatorias`, `useCrearConvocatoria`, `useEditarConvocatoria`, `useCerrarConvocatoria`, `useImportarAlumnos`.
- [x] 7.3 Crear `features/coloquios/schemas.ts` (Zod) para crear/editar convocatoria (días y cupos).
- [x] 7.4 Implementar el panel de métricas (alumnos, instancias activas, reservas, notas).
- [x] 7.5 Implementar el formulario de creación/edición/cierre de convocatoria.
- [x] 7.6 Implementar la importación de alumnos a una convocatoria.
- [x] 7.7 Implementar el listado de convocatorias con métricas operativas y acciones.
- [x] 7.8 Ensamblar `features/coloquios/pages/ColoquiosPage.tsx`.

## 8. Setup de cuatrimestre (FL-03)

- [x] 8.1 Definir `features/setup-cuatrimestre/types.ts` y los hooks de programas (`useProgramasApi`) y fechas académicas (`useFechasAcademicasApi`) sobre `/api/programas` y `/api/fechas-academicas`.
- [x] 8.2 Implementar la gestión de programas (subir/asociar + listado).
- [x] 8.3 Implementar la gestión de fechas de evaluaciones (alta/edición + listado tabular).
- [x] 8.4 Implementar la página orquestadora con stepper que encadena cohorte → clonar equipo → asignación masiva → vigencias → programas → fechas → aviso de bienvenida, reutilizando los hooks de las features previas.
- [x] 8.5 Soportar pasos opcionales / salto de paso sin bloquear el flujo.
- [x] 8.6 Ensamblar `features/setup-cuatrimestre/pages/SetupCuatrimestrePage.tsx`.

## 9. Tests (componentes / integración con mocks)

- [x] 9.1 Tests de equipos: ABM (listado + asignación masiva) y clonado (incluyendo `ids_creados: []`) con `apiClient` mockeado.
- [x] 9.2 Tests de avisos: publicación de aviso (scope condicional + vigencia inválida) y acknowledgment.
- [x] 9.3 Tests de tareas: workflow de estados y comentario en hilo.
- [x] 9.4 Tests de monitores: filtros aplicados (incluyendo rango de fechas) y "Limpiar".
- [x] 9.5 Tests de coloquios: creación de convocatoria y render de métricas.
- [x] 9.6 Verificar que la suite de tests del frontend pasa en verde y no hay `any` ni fetch directo en componentes.

## 10. Cierre

- [x] 10.1 Verificar visibilidad por permiso de cada ítem de menú y ruta (sesión sin permiso no ve la feature).
- [x] 10.2 Documentar en el código cualquier endpoint faltante o `response_model=dict` cuya forma se asumió, y reportar blockers si aplica.
- [ ] 10.3 Marcar C-23 como completado en `CHANGES.md` cuando todo pase (paso de archive).
