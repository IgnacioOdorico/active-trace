## ADDED Requirements

### Requirement: El sistema SHALL permitir crear asignaciones
Una asignación vincula un usuario con un rol dentro de un contexto académico (materia, carrera, cohorte, comisiones).
Los roles permitidos SON: PROFESOR, TUTOR, COORDINADOR, NEXO, ADMIN, FINANZAS.
Las comisiones SON una lista de texto (puede ser vacía).
`responsable_id` ES opcional y referencia a otro Usuario (jerarquía).
`desde` ES obligatorio, `hasta` ES opcional (nulo = abierta).

#### Scenario: Crear asignación exitosa
- **WHEN** se envía POST /api/asignaciones con usuario_id, rol=PROFESOR, materia_id, cohorte_id, comisiones=["A"], desde=fecha-valida
- **THEN** el sistema crea la asignación y responde 201
- **AND** estado_vigencia es "Vigente" si la fecha actual está dentro del rango

#### Scenario: Crear asignación sin permiso retorna 403
- **WHEN** se envía POST /api/asignaciones sin el permiso `equipos:asignar`
- **THEN** el sistema retorna 403 Forbidden

#### Scenario: Crear asignación con rol inválido retorna 422
- **WHEN** se envía POST /api/asignaciones con rol="INEXISTENTE"
- **THEN** el sistema retorna 422 Unprocessable Entity

### Requirement: El sistema SHALL permitir listar asignaciones con filtros
GET /api/asignaciones DEBE soportar filtros por: usuario_id, materia_id, carrera_id, cohorte_id, rol, estado_vigencia.
Paginación: `page`, `page_size` (max 100), `order_by`, `order_dir`.

#### Scenario: Listar asignaciones por usuario
- **WHEN** se envía GET /api/asignaciones?usuario_id={id}
- **THEN** el sistema retorna todas las asignaciones de ese usuario en el tenant

#### Scenario: Listar asignaciones filtra por tenant
- **WHEN** Tenant A lista asignaciones
- **THEN** ninguna asignación de Tenant B aparece en los resultados

### Requirement: El sistema SHALL derivar estado_vigencia desde las fechas
`estado_vigencia` NO se almacena en DB. Se calcula en el service layer comparando `desde`/`hasta` con la fecha actual.

#### Scenario: Asignación vigente
- **WHEN** la fecha actual está entre desde y hasta (o hasta es nulo)
- **THEN** estado_vigencia = "Vigente"

#### Scenario: Asignación vencida
- **WHEN** la fecha actual es posterior a hasta
- **THEN** estado_vigencia = "Vencida"

### Requirement: El sistema SHALL permitir actualizar y eliminar asignaciones
PATCH /api/asignaciones/{id} para modificar campos: comisiones, responsable_id, desde, hasta, rol.
DELETE /api/asignaciones/{id} como soft delete (no físico).

#### Scenario: Actualizar vigencia de asignación
- **WHEN** se envía PATCH /api/asignaciones/{id} con {hasta: nueva-fecha}
- **THEN** el sistema actualiza y recalcula estado_vigencia

#### Scenario: Soft delete de asignación
- **WHEN** se envía DELETE /api/asignaciones/{id}
- **THEN** el sistema marca deleted_at
- **AND** la asignación no aparece en listados GET
- **AND** el registro persiste en DB (histórico)

#### Scenario: Actualizar asignación inexistente retorna 404
- **WHEN** se envía PATCH /api/asignaciones/{uuid-inexistente}
- **THEN** el sistema retorna 404 NotFound
