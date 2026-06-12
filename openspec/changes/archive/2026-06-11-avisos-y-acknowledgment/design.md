## Context

C-06 (`estructura-academica`) estableció los modelos Carrera, Cohorte, Materia que este change necesita como contexto de alcance. El proyecto ya cuenta con EntityMeta mixin, BaseRepository, AuditLogService, y el patrón Clean Architecture consolidado. Sobre esa base, este change implementa F3.5 (tablón de avisos) + FL-09: publicar avisos segmentados por audiencia con vigencia programada y acuse de recibo opcional.

El sistema actual no tiene ningún mecanismo de comunicación institucional interna. Los avisos cubren una necesidad transversal a todos los roles: desde un comunicado global del ADMIN hasta una advertencia de cohorte específica publicada por el COORDINADOR.

## Goals / Non-Goals

**Goals:**
- Modelos ORM `Aviso` y `AcknowledgmentAviso` con `EntityMeta` y SQLAlchemy 2.0 async.
- ABM completo de avisos con alcance (Global/PorMateria/PorCohorte/PorRol), severidad, vigencia programada, orden y requiere_ack.
- Endpoint de visualización que filtra avisos según perfil del usuario autenticado: tenant, roles, materias/cohortes asignadas, ventana de vigencia.
- Endpoint de acknowledgment con idempotencia y contadores derivados desde la tabla.
- Endpoints REST `/api/avisos/*` con dos permisos: `avisos:publicar` (COORD/ADMIN) y `avisos:ver` (todos).
- Audit log con códigos `AVISO_PUBLICAR`, `AVISO_EDITAR`, `AVISO_ELIMINAR`.
- Tests de ABM, filtrado por perfil, acknowledgment, contadores, permisos.

**Non-Goals:**
- No se implementa frontend de avisos (solo API).
- No se implementan notificaciones push ni emails al publicar un aviso.
- No se implementan avisos programados (publicación futura automática) — el aviso se crea con `inicio_en` y es visible cuando la fecha llega.
- No se implementan avisos con destino a alumnos específicos (solo por alcance: Global/Materia/Cohorte/Rol).
- No se implementa edición masiva de avisos.

## Decisions

### D1: Filtrado server-side de avisos visibles
- **Decisión**: El endpoint `GET /api/avisos` recibe el usuario autenticado y filtra en el servicio: selecciona avisos activos, dentro de vigencia, que coinciden con el rol del usuario y su contexto (materias/cohortes donde está asignado).
- **Alternativa considerada**: Envío de todos los avisos al cliente y filtrado client-side.
- **Razón**: El filtrado server-side evita exponer avisos que no corresponden al usuario y reduce la transferencia de datos. El cliente solo ve los avisos que debe ver.

### D2: Acknowledgment como registro independiente con contadores derivados
- **Decisión**: Cada confirmación de lectura es un registro en `AcknowledgmentAviso`. Los contadores (total_acks, total_visitas) se calculan con COUNT sobre la tabla. No se denormalizan en `Aviso`.
- **Alternativa considerada**: Campo contador denormalizado en `Aviso` que se incrementa con cada ack.
- **Razón**: Consistencia con el principio de contadores derivados del proyecto. Evita problemas de concurrencia y datos inconsistentes. El costo de COUNT es despreciable para el volumen esperado de avisos.

### D3: Idempotencia en acknowledgment
- **Decisión**: El endpoint `POST /api/avisos/{id}/ack` es idempotente: si el usuario ya confirmó, retorna éxito sin crear duplicado. Se implementa con `INSERT ... ON CONFLICT DO NOTHING` o verificación previa.
- **Alternativa considerada**: Rechazar con 409 si ya confirmó.
- **Razón**: El frontend puede re-enviar la confirmación sin riesgo de error. La idempotencia simplifica la experiencia de usuario.

### D4: Dos permisos separados para gestión y lectura
- **Decisión**: `avisos:publicar` protege los endpoints de ABM (POST/PUT/DELETE). `avisos:ver` protege GET (lectura). `avisos:publicar` se asigna a COORDINADOR y ADMIN; `avisos:ver` a todos los roles.
- **Alternativa considerada**: Un solo permiso `avisos:gestionar` para todo.
- **Razón**: La lectura de avisos debe estar disponible para todos los roles (incluyendo ALUMNO, TUTOR, PROFESOR). Separar permisos permite que ALUMNO vea avisos sin poder gestionarlos.

### D5: Soft delete en Aviso (nunca borrado físico)
- **Decisión**: Los avisos usan soft delete (`deleted_at`) del EntityMeta. El endpoint DELETE marca como borrado lógico. Los queries de listado excluyen automáticamente borrados.
- **Alternativa considerada**: Borrado físico o columna `activo` booleana.
- **Razón**: Consistencia con el resto del modelo (todos los modelos usan soft delete). El campo `activo` ya existe como atributo de negocio (para preparar avisos antes de publicarlos), pero no reemplaza al soft delete.

### D6: Un solo servicio AvisoService con toda la lógica
- **Decisión**: Un `AvisoService` que inyecta `AvisoRepository`, `AcknowledgmentAvisoRepository` y `AuditLogService`. Maneja ABM, filtrado por perfil, y acknowledgment.
- **Alternativa considerada**: Separar en `AvisoGestionService` y `AvisoLecturaService`.
- **Razón**: El módulo es pequeño y cohesivo. Un solo servicio evita duplicación y simplifica la inyección de dependencias.

## Risks / Trade-offs

- **[Riesgo] Performance del filtrado por perfil**: si un usuario está asignado a muchas materias/cohortes, el query de avisos visibles podría ser lento. → **Mitigación**: índices compuestos en `(tenant_id, activo, inicio_en, fin_en)` y en `(tenant_id, usuario_id)` para asignaciones. Paginación obligatoria.
- **[Riesgo] Avisos sin alcance definido**: si se crea un aviso con `rol_destino = null` pero alcance PorRol, puede no mostrarse a nadie. → **Mitigación**: validación en el servicio que verifica coherencia entre alcance y campos de contexto (si alcance=PorMateria, materia_id es requerido; si alcance=PorRol, rol_destino es requerido; etc.).
- **[Trade-off] Sin edición del cuerpo después de publicado**: el diseño actual no impide editar el cuerpo del aviso después de publicado. → **Razón**: El soft delete permite "despublicar" un aviso incorrecto y crear uno nuevo. La edición de `cuerpo` se permite pero queda registrada en audit log.
