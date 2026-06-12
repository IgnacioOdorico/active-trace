## Context

Activia-Trace necesita un módulo de liquidaciones y honorarios para procesar pagos docentes. El sistema ya tiene:
- Clean Architecture con FastAPI + SQLAlchemy 2.0 async
- Multi-tenant con scope por tenant_id en todas las queries
- Sistema de permisos granulares (módulo:acción) con wildcard `*`
- Auditoría con modelo AuditLog
- Roles existentes FINANZAS y NEXO con permisos semilla para liquidaciones

Este change agrega 4 modelos (SalarioBase, SalarioPlus, Liquidacion, Factura), endpoints REST, lógica de cálculo financiero (RN-34), manejo de archivos PDF y separación contable.

## Goals / Non-Goals

**Goals:**
- Modelar grilla salarial con vigencia temporal (SalarioBase y SalarioPlus)
- Calcular liquidaciones por (cohorte × mes) aplicando RN-34
- Permitir cierre de liquidación con inmutabilidad posterior
- Gestionar facturas de docentes que facturan (carga PDF, estados)
- Separación contable en 3 segmentos: general, NEXO, facturantes
- Auditoría obligatoria en cada acción financiera

**Non-Goals:**
- No se implementa pago real ni integración con bancos
- No se implementa workflow de aprobación multi-paso (cierre es directo)
- No se implementa exportación contable a sistemas externos (queda para change futuro)
- No se implementa generación de recibos PDF

## Decisions

### D1: 4 tablas separadas en vez de una tabla polimórfica
Separar SalarioBase, SalarioPlus, Liquidacion y Factura en tablas individuales, cada una con su propio modelo SQLAlchemy. Esto sigue el patrón existente del proyecto (1 modelo = 1 tabla) y evita la complejidad de herencia/polimorfismo. La desventaja es más tablas, pero cada una tiene semántica distinta y ciclo de vida diferente.

### D2: Cálculo de liquidación como servicio transaccional
La lógica de RN-34 vive en `services/liquidaciones.py` como una función `calcular_liquidacion(cohorte_id, periodo)` que:
1. Obtiene todas las comisiones activas del cohorte en el período
2. Agrupa por usuario_id y rol
3. Para cada docente: calcula base (SalarioBase vigente), calcula plus por grupo (SalarioPlus × N comisiones en ese grupo), suma total
4. Persiste las Liquidaciones en una sola transacción
5. Registra audit LIQUIDACION_CALCULAR
La transaccionalidad asegura que no quede un cálculo a medias.

### D3: Vigencia temporal con `desde` incluido y `hasta` abierto (NULL = vigente)
Se usa el patrón `desde <= fecha_liq < hasta` con `hasta` nullable para indicar "vigencia abierta". Una constraint CHECK a nivel DB o validación en servicio asegura que no haya dos registros vigentes del mismo tipo superpuestos. Se elige `hasta` exclusivo para evitar ambigüedades en fechas exactas.

### D4: File upload de factura con almacenamiento en sistema de archivos
Las facturas PDF se almacenan en el sistema de archivos local (`/data/facturas/{tenant_id}/{periodo}/`) con metadatos en DB. No se usa S3 en esta iteración porque no hay infraestructura cloud. El nombre de archivo incluye timestamp para evitar colisiones. El tamaño se registra en KB en la DB. Migración futura: mover a S3/CDN.

### D5: Soft-delete NO aplica a datos financieros
Los modelos Liquidacion y Factura NO usan soft-delete (no tienen `deleted_at`). Los datos financieros no se eliminan, se cierran (inmutable) o se anulan con contra-asientos. SalarioBase y SalarioPlus sí pueden tener soft-delete porque son configuración.

### D6: Permisos granulares con 6 nuevas acciones
Se agregan permisos `liquidaciones:calcular`, `liquidaciones:cerrar`, `liquidaciones:exportar`, `liquidaciones:configurar-salarios`, más `facturas:cargar`, `facturas:abonar`. El wildcard `liquidaciones:*` y `facturas:*` existentes cubren a FINANZAS. NEXO hereda `liquidaciones:ver` y `facturas:ver`.

### D7: Separación contable por flag + rol
`Liquidacion.es_nexo` distingue NEXO del general. `Liquidacion.excluido_por_factura` señala docentes que facturan (no generan pago directo). KPIs se calculan filtrando por estos flags. `Factura` es tabla separada con sus propios estados (Pendiente/Abonada).

## Risks / Trade-offs

- **[Cálculo incorrecto]** La fórmula RN-34 depende de datos de comisiones y grilla salarial. Si la grilla tiene datos incorrectos, la liquidación calcula mal. → **Mitigación**: preview de cálculo antes de cerrar; tests exhaustivos por cada caso de RN-34.
- **[Inmutabilidad]** Una vez cerrada, la liquidación no puede modificarse. Si se descubre un error, hay que hacer una liquidación complementaria. → **Mitigación**: workflow de preview y confirmación; documentar proceso de rectificación.
- **[File upload sin S3]** Almacenamiento local no escala horizontalmente. → **Mitigación**: aceptado para MVP; el path de archivo es configurable.
- **[Performance en cálculo masivo]** Si hay 500+ comisiones activas, calcular puede ser lento. → **Mitigación**: el cálculo corre en el worker (tarea asíncrona) si es necesario; timeout configurable.
- **[Solapamiento de grilla]** Dos registros vigentes simultáneos para el mismo rol. → **Mitigación**: validación en servicio al crear/editar con query explícita de solapamiento; unique constraint composite no alcanza por la naturaleza temporal.
