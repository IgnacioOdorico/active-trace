## ADDED Requirements

### Requirement: El sistema SHALL modelar SalarioBase con monto por rol y vigencia temporal
`SalarioBase` define el monto base para cada rol docente (PROFESOR, TUTOR, NEXO, COORDINADOR, ALL) con un período de vigencia. Solo puede haber una entrada vigente por rol en un instante dado.

#### Scenario: Crear salario base para un rol
- **WHEN** se crea un SalarioBase con rol=PROFESOR, monto=500.00, desde=2026-01-01
- **THEN** el sistema persiste el registro con hasta=null (vigencia abierta)

#### Scenario: Dos salarios base para el mismo rol con fechas no solapadas
- **WHEN** existe SalarioBase(rol=PROFESOR, monto=500.00, desde=2026-01-01, hasta=2026-06-30)
- **AND** se crea SalarioBase(rol=PROFESOR, monto=550.00, desde=2026-07-01)
- **THEN** ambos registros son válidos por no solapar sus vigencias

#### Scenario: Rechazar salario base con solapamiento
- **WHEN** existe SalarioBase(rol=PROFESOR, monto=500.00, desde=2026-01-01, hasta=null)
- **AND** se intenta crear SalarioBase(rol=PROFESOR, monto=550.00, desde=2026-03-01)
- **THEN** el sistema rechaza con error de solapamiento temporal

#### Scenario: Cerrar vigencia abierta (setear hasta)
- **WHEN** se actualiza SalarioBase(rol=TUTOR, hasta=null) seteando hasta=2026-12-31
- **THEN** el sistema persiste el cambio y ese registro deja de ser la entrada vigente

### Requirement: El sistema SHALL modelar SalarioPlus como complemento por grupo de materias y rol
`SalarioPlus` es un adicional que se aplica a docentes con comisiones en materias de un grupo específico (ej: "PROG", "BD"). Un docente puede acumular plus de distintos grupos.

#### Scenario: Crear plus salarial para un grupo y rol
- **WHEN** se crea SalarioPlus con grupo="PROG", rol=PROFESOR, monto=100.00, desde=2026-01-01
- **THEN** el sistema persiste el registro

#### Scenario: Plus con vigencia temporal (desde/hasta)
- **WHEN** se crea SalarioPlus con grupo="BD", rol=TUTOR, monto=50.00, desde=2026-03-01, hasta=2026-12-31
- **THEN** el plus solo aplica para liquidaciones dentro de ese rango

#### Scenario: Mismo grupo y rol con fechas distintas no solapa
- **WHEN** existe SalarioPlus(grupo="PROG", rol=PROFESOR, desde=2026-01-01, hasta=2026-06-30)
- **AND** se crea SalarioPlus(grupo="PROG", rol=PROFESOR, desde=2026-07-01)
- **THEN** ambos son válidos por vigencia no solapada

### Requirement: El sistema SHALL exponer CRUD de grilla salarial solo con permiso `liquidaciones:configurar-salarios`
Solo usuarios con el permiso `liquidaciones:configurar-salarios` pueden crear, modificar o eliminar SalarioBase y SalarioPlus.

#### Scenario: Crear salario base sin permiso retorna 403
- **WHEN** se envía POST /api/v1/salario-base sin permiso `liquidaciones:configurar-salarios`
- **THEN** el sistema retorna 403

#### Scenario: Actualizar plus salarial con permiso retorna 200
- **WHEN** un usuario con permiso `liquidaciones:configurar-salarios` actualiza un SalarioPlus existente
- **THEN** el sistema retorna 200 con el registro actualizado

### Requirement: Las acciones de configuración salarial SHALL generar audit SALARIO_CONFIGURAR
Cada creación, modificación o eliminación de SalarioBase o SalarioPlus genera un registro de auditoría.

#### Scenario: Crear salario base genera audit
- **WHEN** se crea un SalarioBase
- **THEN** el sistema registra audit con accion="SALARIO_CONFIGURAR" y detalle con tipo="salario_base" y los valores creados
