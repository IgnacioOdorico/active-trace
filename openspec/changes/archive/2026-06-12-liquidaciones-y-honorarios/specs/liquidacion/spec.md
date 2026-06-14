## ADDED Requirements

### Requirement: El sistema SHALL calcular liquidaciones por (cohorte × mes) aplicando RN-34
La liquidación se calcula por cohorte y período (AAAA-MM). Para cada docente con comisiones activas en ese cohorte y mes, se determina:
- Rol del docente en ese cohorte
- Monto base = SalarioBase vigente para ese rol en la fecha del período
- Plus por grupo = para cada grupo de materias donde el docente tenga comisiones, se suma SalarioPlus(grupo, rol) vigente × cantidad de comisiones en ese grupo
- Total = Base + Σ(Plus)

#### Scenario: Calcular liquidación de profesor con comisiones en PROG
- **WHEN** un profesor tiene 2 comisiones en materias del grupo PROG en cohorte C1
- **AND** SalarioBase(rol=PROFESOR, monto=500.00) está vigente
- **AND** SalarioPlus(grupo="PROG", rol=PROFESOR, monto=100.00) está vigente
- **AND** se calcula liquidación para (C1, 2026-06)
- **THEN** el sistema crea Liquidacion con monto_base=500.00, monto_plus=200.00 (100×2), total=700.00

#### Scenario: Calcular liquidación sin plus aplicable
- **WHEN** un profesor tiene comisiones pero ninguna materia pertenece a un grupo con SalarioPlus vigente
- **THEN** monto_plus=0.00 y total=monto_base

#### Scenario: Calcular liquidación con múltiples grupos
- **WHEN** un profesor tiene 1 comisión en PROG (plus 100) y 3 comisiones en BD (plus 50)
- **THEN** monto_plus = (100×1) + (50×3) = 250.00

#### Scenario: Re-calcular liquidación ya cerrada retorna error
- **WHEN** se intenta calcular liquidación para un (cohorte, periodo) que ya tiene liquidaciones cerradas
- **THEN** el sistema retorna error 409 indicando que el período ya está cerrado

#### Scenario: Calcular liquidación sin comisiones activas retorna vacío
- **WHEN** no hay comisiones activas para el cohorte en el período
- **THEN** el sistema retorna 200 con lista vacía de liquidaciones generadas

### Requirement: El sistema SHALL listar liquidaciones del período con permiso `liquidaciones:ver`
Usuarios con `liquidaciones:ver` (o wildcard `liquidaciones:*`) pueden ver las liquidaciones de un período, filtradas por cohorte y mes.

#### Scenario: Ver liquidaciones de un período
- **WHEN** se envía GET /api/v1/liquidaciones?cohorte_id=X&periodo=2026-06
- **AND** el usuario tiene permiso `liquidaciones:ver`
- **THEN** el sistema retorna 200 con la lista de liquidaciones del período

#### Scenario: Ver liquidaciones sin permiso retorna 403
- **WHEN** se envía GET /api/v1/liquidaciones sin permiso `liquidaciones:ver`
- **THEN** el sistema retorna 403

### Requirement: El sistema SHALL cerrar una liquidación haciéndola inmutable (RN-22)
Cerrar una liquidación cambia su estado a "Cerrada". Una vez cerrada:
- No puede modificarse ni recalcularse
- El estado es irreversible (no puede reabrirse)

#### Scenario: Cerrar liquidación abierta
- **WHEN** se envía POST /api/v1/liquidaciones/{id}/cerrar con estado=Abierta
- **AND** el usuario tiene permiso `liquidaciones:cerrar`
- **THEN** el sistema cambia estado a Cerrada y retorna 200

#### Scenario: Cerrar liquidación ya cerrada retorna error
- **WHEN** se envía POST /api/v1/liquidaciones/{id}/cerrar sobre una liquidación ya Cerrada
- **THEN** el sistema retorna 409

#### Scenario: Cerrar sin permiso retorna 403
- **WHEN** se envía POST /api/v1/liquidaciones/{id}/cerrar sin permiso `liquidaciones:cerrar`
- **THEN** el sistema retorna 403

#### Scenario: Cerrar genera audit
- **WHEN** se cierra una liquidación
- **THEN** el sistema registra audit con accion="LIQUIDACION_CERRAR"

### Requirement: El sistema SHALL exponer historial de liquidaciones
Usuarios con `liquidaciones:ver` pueden consultar liquidaciones de períodos anteriores, tanto abiertas como cerradas.

#### Scenario: Ver historial por período
- **WHEN** se envía GET /api/v1/liquidaciones/historial?cohorte_id=X&desde=2026-01&hasta=2026-06
- **THEN** el sistema retorna las liquidaciones de esos meses, ordenadas por período descendente

#### Scenario: Ver historial filtrado por estado
- **WHEN** se envía GET /api/v1/liquidaciones/historial?estado=Cerrada
- **THEN** el sistema retorna solo liquidaciones cerradas

### Requirement: El sistema SHALL generar audit LIQUIDACION_CALCULAR al calcular liquidaciones
Cada cálculo de liquidación (nuevo o re-cálculo de abiertas) genera un registro de auditoría.

#### Scenario: Calcular genera audit
- **WHEN** se ejecuta el cálculo de liquidación para un cohorte y período
- **THEN** el sistema registra audit con accion="LIQUIDACION_CALCULAR" y detalle incluyendo cohorte_id, periodo y cantidad de liquidaciones generadas
