## ADDED Requirements

### Requirement: Página orquestadora del setup de cuatrimestre (FL-03)
La feature SHALL ofrecer al COORDINADOR una página guía que encadena los pasos de inicio de período: crear cohorte, clonar equipo docente, ajustar asignaciones (alta masiva), ajustar vigencias, cargar programas de materia, cargar fechas de evaluaciones y publicar el aviso de bienvenida. Cada paso SHALL reutilizar los hooks de las features de equipos, avisos, programas y fechas; la página NO mantiene estado de servidor propio.

#### Scenario: Recorrido completo del setup
- **WHEN** el coordinador avanza por los pasos del flujo
- **THEN** cada paso dispara el endpoint del dominio correspondiente y la página marca el paso como completado

#### Scenario: Pasos opcionales / salto de paso
- **WHEN** el coordinador omite un paso no obligatorio (p.ej. ya existe la cohorte)
- **THEN** la página permite continuar al siguiente paso sin bloquear el flujo

### Requirement: Gestión de programas de materia
La feature SHALL permitir subir y asociar el programa oficial de una materia para una combinación carrera × cohorte mediante `POST /api/programas`, y listarlos (`GET /api/programas`).

#### Scenario: Subir programa
- **WHEN** el coordinador asocia un documento de programa a materia × carrera × cohorte
- **THEN** la feature lo envía y aparece en el listado de programas

### Requirement: Gestión de fechas de evaluaciones
La feature SHALL permitir registrar y editar fechas de parciales, TP y coloquios por materia × cohorte × número mediante `POST /api/fechas-academicas` y `PATCH /api/fechas-academicas/{id}`, con vista de listado tabular.

#### Scenario: Registrar fecha de evaluación
- **WHEN** el coordinador registra una fecha de parcial para una materia y cohorte
- **THEN** la feature la envía y la fecha aparece en el listado tabular

### Requirement: Publicar aviso de bienvenida desde el setup
El paso final del setup SHALL permitir publicar un aviso con alcance a la nueva cohorte reutilizando la feature de avisos (`POST /api/avisos`).

#### Scenario: Aviso de bienvenida
- **WHEN** el coordinador publica el aviso de bienvenida acotado a la nueva cohorte
- **THEN** la feature lo envía y el setup queda completo
