## Context

C-07 creó el modelo `Usuario` con PII cifrada. Ahora necesitamos el padrón de alumnos: los estudiantes que cursan cada materia. El modelo es versionado — cada importación crea una nueva versión sin destruir la anterior. Además, el sistema debe integrarse con Moodle WS para sincronización automática.

No existe aún un cliente Moodle en el proyecto. `VersionPadron` y `EntradaPadron` son modelos nuevos.
La importación manual (`.xlsx`/`.csv`) es el fallback cuando Moodle no está disponible.

## Goals / Non-Goals

**Goals:**
- Modelos `VersionPadron` y `EntradaPadron` con versionado (solo una activa por materia×cohorte).
- Import desde archivo `.xlsx`/`.csv` con vista previa (F1.3, F1.4).
- Integración Moodle WS: sync nocturna + on-demand con reintentos (máx 3, backoff exponencial).
- Vaciar datos de materia (F1.5, RN-04).
- Audit `PADRON_CARGAR`.
- `Migración 007: version_padron, entrada_padron`.

**Non-Goals:**
- No se implementa la importación de calificaciones (C-10).
- No se sincronizan actividades del LMS — solo padrón de alumnos.
- No se crean cuentas de usuario para alumnos sin cuenta (se deja `usuario_id` nulo).

## Decisions

### D1: Versionado por activación explícita
- **Decisión**: Importar un padrón lo crea en estado inactivo. El usuario debe activarlo explícitamente, lo que desactiva la versión anterior.
- **Razón**: Permite revisar la vista previa antes de que los cambios sean efectivos. El activar desactiva automáticamente la versión previa para la misma materia×cohorte.

### D2: Cliente Moodle WS como módulo separado
- **Decisión**: `integrations/moodle_ws.py` es una clase independiente con sus propios métodos de sync.
- **Alternativa considerada**: Integrar la lógica en el service de padrón.
- **Razón**: El cliente Moodle puede tener su propio ciclo de vida (reintentos, caché, logging). Separarlo permite testearlo independientemente con mocks.

### D3: Alumnos sin cuenta de usuario
- **Decisión**: `EntradaPadron.usuario_id` es nullable. Si el alumno no tiene cuenta en el sistema, se almacena solo con nombre, apellidos y email cifrado.
- **Razón**: El padrón puede importarse antes de que los alumnos tengan cuentas. La vinculación se hace después (manual o automática).

## Risks / Trade-offs

- **[Riesgo] Moodle WS caído**: si Moodle no responde, el import manual debe funcionar como fallback. → **Mitigación**: el service intenta Moodle primero; si falla después de 3 reintentos, permite subir archivo manual.
- **[Riesgo] PII en archivos subidos**: el `.xlsx` puede contener emails de alumnos. → **Mitigación**: el service cifra el email antes de persistir. El archivo original no se almacena.
- **[Trade-off] Sin validación de columnas del archivo**: se asume una convención de columnas específica. Archivos con formato distinto fallarán con error claro.
