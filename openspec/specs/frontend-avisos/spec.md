## ADDED Requirements

### Requirement: ABM de avisos
La feature SHALL permitir al usuario con permiso `avisos:publicar` crear, editar y eliminar avisos mediante `POST /api/avisos`, `PATCH /api/avisos/{id}` y `DELETE /api/avisos/{id}`. El formulario SHALL capturar alcance (global / por materia / por cohorte / por rol), contexto (materia/cohorte cuando el alcance no es global), roles destinatarios, severidad, título y cuerpo, ventana de vigencia (inicio/fin), orden de prioridad, estado activo/inactivo y requiere_ack. La validación SHALL usar React Hook Form + Zod.

#### Scenario: Crear aviso global
- **WHEN** el usuario completa un aviso de alcance global con vigencia válida y publica
- **THEN** la feature envía `POST /api/avisos`, muestra confirmación e invalida la lista de gestión

#### Scenario: Scope condicional requerido
- **WHEN** el usuario elige alcance "por cohorte" pero no selecciona cohorte
- **THEN** el schema bloquea el envío y muestra el error de validación

#### Scenario: Vigencia inválida
- **WHEN** la fecha de inicio es posterior a la de fin
- **THEN** el formulario muestra error y no envía el request

### Requirement: Vista de gestión con contadores de acknowledgment
La feature SHALL mostrar el listado de gestión de avisos desde `GET /api/avisos/gestion`, incluyendo el contador de confirmaciones de lectura derivado del backend, ordenado por prioridad.

#### Scenario: Listado de gestión con contadores
- **WHEN** el usuario abre la vista de gestión
- **THEN** la feature renderiza cada aviso con su scope, severidad, ventana de vigencia y cantidad de acknowledgments

### Requirement: Confirmación de lectura de aviso
La feature SHALL permitir a cualquier usuario destinatario acusar recibo de un aviso que requiere confirmación mediante `POST /api/avisos/{id}/ack`, tras lo cual el aviso deja de mostrarse al usuario.

#### Scenario: Acknowledgment exitoso
- **WHEN** el usuario confirma la lectura de un aviso con requiere_ack
- **THEN** la feature envía el ack y el aviso desaparece de la vista del usuario
