## Why

Activia-Trace necesita gestionar liquidaciones de honorarios docentes: calcular montos base por rol, aplicar plus por categoría, cerrar períodos contables y administrar facturas de docentes que facturan. Sin este sistema, FINANZAS no puede procesar pagos ni cerrar meses. Este change implementa el módulo completo de liquidaciones y honorarios.

Governance: **CRITICAL** — toda operación involucra datos financieros. Cierre de liquidación es inmutable. Auditoría obligatoria en cada acción.

## What Changes

- **4 nuevos modelos DB**: `SalarioBase`, `SalarioPlus`, `Liquidacion`, `Factura` con migrations Alembic
- **Grilla salarial**: CRUD de SalarioBase (monto por rol con vigencia temporal) y SalarioPlus (adicional por grupo×rol)
- **Cálculo de liquidaciones**: endpoint que genera liquidaciones por (cohorte×mes) aplicando RN-34: Total = Base(rol vigente) + Σ(Plus(categoria,rol) × N_comisiones)
- **Cierre de liquidación**: marca inmutable, impide re-cálculo o modificación posterior
- **Gestión de facturas**: carga de PDF, estados Pendiente/Abonada, tracking de archivo
- **Separación contable**: 3 segmentos (general, NEXO, facturantes) con KPIs separados
- **Auditoría**: acciones LIQUIDACION_CALCULAR, LIQUIDACION_CERRAR, FACTURA_CARGAR, FACTURA_ABONAR, SALARIO_CONFIGURAR
- **Nuevos permisos granulares**: `liquidaciones:calcular`, `liquidaciones:cerrar`, `liquidaciones:ver`, `liquidaciones:exportar`, `liquidaciones:configurar-salarios`, `facturas:cargar`, `facturas:abonar`
- Seed actualizado de roles FINANZAS y NEXO con los nuevos permisos
- Endpoints REST bajo `/api/v1/liquidaciones/` y `/api/v1/facturas/`
- Tests de cálculo, cierre, permisos, idempotencia y carga de archivos

No hay cambios BREAKING. Los permisos existentes `liquidaciones:*`, `liquidaciones:ver`, `facturas:*`, `facturas:ver` en seed se mantienen.

## Capabilities

### New Capabilities

- `grilla-salarial`: administración de SalarioBase (monto por rol con vigencia temporal) y SalarioPlus (adicional por grupo×rol). CRUD con validación de solapamiento temporal.
- `liquidacion`: vista del período, cálculo automático por (cohorte×mes) aplicando RN-34, cierre con inmutabilidad, historial de liquidaciones cerradas.
- `factura`: gestión de facturas de docentes que facturan: carga de PDF, detalle, estados Pendiente/Abonada, tracking de archivo.
- `separacion-contable`: KPIs y reportes separados por segmento (general, NEXO, facturantes), excluyendo docentes facturantes de liquidación general.

### Modified Capabilities

<!-- Ninguna: es un módulo nuevo, no hay specs previos que modificar. -->

## Impact

- **Nuevos modelos**: `backend/app/models/salario_base.py`, `salario_plus.py`, `liquidacion.py`, `factura.py`
- **Esquemas Pydantic**: schemas de request/response para cada modelo
- **Repositorios**: `backend/app/repositories/` para cada entidad con scope tenant
- **Servicios**: `backend/app/services/liquidaciones.py` con la lógica de cálculo (RN-34)
- **Routers**: `backend/app/api/v1/routers/liquidaciones.py` y `facturas.py`
- **3 archivos de specs**: `openspec/changes/liquidaciones-y-honorarios/specs/` (grilla-salarial, liquidacion, factura)
- **Migration Alembic**: nueva migración con las 4 tablas
- **Seed actualizado**: permisos granulares y descripciones en `core/seed.py`
- **Test files**: tests para cálculo de liquidación, cierre, permisos, facturas
- **Dependencias**: posible necesidad de `python-multipart` para upload de PDF (verificar si ya está)
