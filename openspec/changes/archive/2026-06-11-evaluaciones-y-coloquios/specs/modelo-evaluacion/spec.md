## ADDED Requirements

### Requirement: Modelo ORM Evaluacion (tabla evaluacion)
El sistema SHALL tener un modelo ORM `Evaluacion` (tabla `evaluacion`) con los siguientes campos:
- `id`: UUID (PK, default gen_random_uuid())
- `tenant_id`: UUID (FK → Tenant)
- `materia_id`: UUID (FK → Materia)
- `cohorte_id`: UUID (FK → Cohorte)
- `tipo`: String(20) — Parcial | TP | Coloquio | Recuperatorio
- `instancia`: String(200) — denominación libre (ej: "Coloquio Final")
- `dias_disponibles`: Integer — ventana de inscripción en días

#### Scenario: Crear evaluacion exitosamente
- **WHEN** un COORDINADOR crea una evaluación con materia_id, cohorte_id, tipo="Coloquio", instancia="Coloquio Final", dias_disponibles=5
- **THEN** el sistema persiste el registro con id UUID, tenant_id del usuario, y todos los campos provistos

#### Scenario: Evaluacion require materia y cohorte
- **WHEN** se intenta crear una evaluación sin materia_id o sin cohorte_id
- **THEN** el sistema rechaza la operación con error de validación

#### Scenario: Tipo validado contra enum
- **WHEN** se intenta crear una evaluación con tipo "Examen" (no válido)
- **THEN** el sistema rechaza la operación con error de validación

### Requirement: Modelo ORM EvaluacionDia (tabla evaluacion_dia)
El sistema SHALL tener un modelo ORM `EvaluacionDia` (tabla `evaluacion_dia`) con los siguientes campos:
- `id`: UUID (PK, default gen_random_uuid())
- `evaluacion_id`: UUID (FK → Evaluacion)
- `fecha`: Date — día concreto de la convocatoria
- `cupo_maximo`: Integer — cupo total para ese día
- `cupos_restantes`: Integer — cupos disponibles (se decrementa al reservar)

#### Scenario: Crear dias de evaluacion exitosamente
- **WHEN** se crea una evaluación con días_disponibles=5 y se generan los días concretos
- **THEN** el sistema crea N registros EvaluacionDia con cupo_maximo y cupos_restantes igual al valor inicial

#### Scenario: Cupo maximo no puede ser negativo
- **WHEN** se intenta crear un EvaluacionDia con cupo_maximo < 1
- **THEN** el sistema rechaza la operación con error de validación

### Requirement: Modelo ORM ReservaEvaluacion (tabla reserva_evaluacion)
El sistema SHALL tener un modelo ORM `ReservaEvaluacion` (tabla `reserva_evaluacion`) con los siguientes campos:
- `id`: UUID (PK, default gen_random_uuid())
- `tenant_id`: UUID (FK → Tenant)
- `evaluacion_dia_id`: UUID (FK → EvaluacionDia)
- `alumno_id`: UUID (FK → Usuario, rol ALUMNO)
- `fecha_hora`: DateTime(timezone=True)
- `estado`: String(20) — Activa | Cancelada

#### Scenario: Crear reserva exitosamente
- **WHEN** un ALUMNO reserva un turno en un día con cupo disponible
- **THEN** el sistema persiste ReservaEvaluacion con id UUID, estado "Activa", fecha_hora actual

#### Scenario: Reserva requiere alumno_id valido
- **WHEN** se intenta crear una reserva con alumno_id que no existe o no es rol ALUMNO
- **THEN** el sistema rechaza la operación con error

### Requirement: Modelo ORM ResultadoEvaluacion (tabla resultado_evaluacion)
El sistema SHALL tener un modelo ORM `ResultadoEvaluacion` (tabla `resultado_evaluacion`) con los siguientes campos:
- `id`: UUID (PK, default gen_random_uuid())
- `tenant_id`: UUID (FK → Tenant)
- `evaluacion_id`: UUID (FK → Evaluacion)
- `alumno_id`: UUID (FK → Usuario)
- `nota_final`: String(20) — numérica o cualitativa

#### Scenario: Crear resultado exitosamente
- **WHEN** un COORDINADOR registra nota_final para un alumno en una evaluación
- **THEN** el sistema persiste ResultadoEvaluacion con id UUID, tenant_id, evaluacion_id, alumno_id, nota_final

#### Scenario: Resultado duplicado reemplaza anterior
- **WHEN** se registra un resultado para un alumno que ya tiene resultado en la misma evaluación
- **THEN** el sistema actualiza el registro existente con la nueva nota_final

#### Scenario: Resultado permite valores cualitativos
- **WHEN** se registra nota_final="Ausente"
- **THEN** el sistema acepta y persiste el valor sin error
