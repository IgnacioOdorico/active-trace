## 1. Migración: tabla mensajes + seed de permisos

- [x] 1.1 Crear migración Alembic `016_mensajes_permisos.py` con tabla `mensajes` (columnas: id, tenant_id, created_at, updated_at, deleted_at, thread_id FK a mensajes.id, remitente_id FK a users.id, destinatario_id FK a users.id, asunto String(200), cuerpo Text, leido Boolean default false) + índices en `(destinatario_id, thread_id)` y `thread_id`
- [x] 1.2 Agregar seed de permisos en la misma migración: `perfil:editar`, `inbox:leer`, `inbox:responder` con descripciones y asignación a roles TUTOR, PROFESOR, COORDINADOR, ADMIN (patrón migración 012)
- [x] 1.3 Agregar entradas a `app/core/seed.py` para los nuevos permisos (PERMISO_DESCRIPTIONS) y asignación a roles (SEED_ROLES)

## 2. Modelo Mensaje

- [x] 2.1 (RED) Escribir test del modelo `Mensaje`: crear instancia con campos obligatorios, verificar herencia EntityMeta (id, tenant_id, deleted_at), verificar thread_id nullable
- [x] 2.2 (GREEN) Implementar `app/models/mensaje.py` con `Mensaje(Base, EntityMeta)` y relaciones a User (remitente, destinatario)
- [x] 2.3 (TRIANGULATE) Test: crear hilo con respuestas, verificar relación thread_id apuntando al raíz

## 3. Repositorio MensajeRepository

- [x] 3.1 (RED) Escribir test de `MensajeRepository.listar_hilos`: insertar varios mensajes, verificar paginación y filtro por destinatario
- [x] 3.2 (GREEN) Implementar `app/repositories/mensaje_repository.py` extendiendo `BaseRepository[Mensaje]` con métodos: `listar_hilos`, `obtener_hilo`, `responder`
- [x] 3.3 (RED) Test de `MensajeRepository.obtener_hilo`: crear hilo con respuestas, verificar que devuelve raíz + respuestas ordenadas
- [x] 3.4 (GREEN) Implementar `obtener_hilo` en repositorio
- [x] 3.5 (TRIANGULATE) Test: responder a hilo crea mensaje con thread_id correcto y remitente/destinatario swappeado

## 4. Servicio y schemas de Perfil

- [x] 4.1 Crear `app/schemas/perfil.py` con `PerfilResponse` (todos los campos del User incluyendo PII desencriptada) y `PerfilUpdate` (solo campos editables: nombre, apellidos, dni, cbu, alias_cbu, banco, regional, email, legajo_profesional, facturador — SIN cuil)
- [x] 4.2 (RED) Escribir test de `PerfilService.obtener`: usuario autenticado obtiene su perfil con PII desencriptada
- [x] 4.3 (GREEN) Implementar `app/services/perfil_service.py` con `PerfilService.obtener(db, user)` que reutiliza `_decrypt_pii` del patrón UsuarioService
- [x] 4.4 (RED) Test de `PerfilService.actualizar`: actualizar nombre y email, verificar cambio persistido y PII encriptada en DB
- [x] 4.5 (GREEN) Implementar `PerfilService.actualizar(db, user, data)`: validar email único por tenant, encriptar PII, update parcial, desencriptar respuesta
- [x] 4.6 (TRIANGULATE) Test: actualizar perfil con email duplicado retorna DomainError("EMAIL_DUPLICADO")

## 5. Servicio InboxService

- [x] 5.1 (RED) Escribir test de `InboxService.listar_hilos`: crear varios hilos para el usuario, verificar paginación y orden
- [x] 5.2 (GREEN) Implementar `app/services/inbox_service.py` con `InboxService` (tenant_id, MensajeRepository) y método `listar_hilos`
- [x] 5.3 (RED) Test de `InboxService.obtener_hilo`: verificar que devuelve hilo completo o EntityNotFoundError
- [x] 5.4 (GREEN) Implementar `InboxService.obtener_hilo` con verificación de pertenencia (remitente o destinatario)
- [x] 5.5 (RED) Test de `InboxService.responder`: responder a hilo, verificar nuevo mensaje con thread_id correcto y remitente/destinatario swappeado
- [x] 5.6 (GREEN) Implementar `InboxService.responder`

## 6. Router de Perfil

- [x] 6.1 (RED) Escribir test de integración: `GET /api/perfil` retorna 200 con datos del usuario autenticado
- [x] 6.2 (GREEN) Implementar `app/routers/perfil.py` con `GET /api/perfil` (guard: `require_permission("perfil:editar")`)
- [x] 6.3 (RED) Test: `PUT /api/perfil` actualiza campos exitosamente
- [x] 6.4 (GREEN) Implementar `PUT /api/perfil` con validación de email duplicado
- [x] 6.5 (TRIANGULATE) Test: PUT /api/perfil con cuil en body retorna 422; PUT sin permiso retorna 403; PUT sin auth retorna 401
- [x] 6.6 Registrar router en `app/main.py` (`app.include_router(perfil_router)`)

## 7. Router de Inbox

- [x] 7.1 (RED) Escribir test de integración: `GET /api/inbox` retorna 200 con lista paginada
- [x] 7.2 (GREEN) Implementar `app/routers/inbox.py` con `GET /api/inbox` (guard: `require_permission("inbox:leer")`)
- [x] 7.3 (RED) Test: `GET /api/inbox/{id}` retorna hilo completo
- [x] 7.4 (GREEN) Implementar `GET /api/inbox/{id}` con EntityNotFoundError → 404
- [x] 7.5 (RED) Test: `POST /api/inbox/{id}/responder` crea respuesta exitosamente
- [x] 7.6 (GREEN) Implementar `POST /api/inbox/{id}/responder` (guard: `require_permission("inbox:responder")`, retorna 201)
- [x] 7.7 (TRIANGULATE) Tests: responder a hilo ajeno retorna 404; sin permiso retorna 403
- [x] 7.8 Registrar router en `app/main.py`

## 8. Verificación de cierre de sesión (F11.3)

- [x] 8.1 Verificar que `POST /api/auth/logout` (C-03) existe, responde 204 con token válido, y el token queda invalidado
- [x] 8.2 Agregar test si no existe: logout con y sin autenticación

## 9. Suite completa

- [x] 9.1 Ejecutar `pytest` y confirmar todos los tests verdes (998 passed, 4 pre-existing failures en test_migration_005.py no relacionados)
- [x] 9.2 Verificar que la migración `016` se ejecuta correctamente (upgrade + downgrade)
