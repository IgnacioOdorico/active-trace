## ADDED Requirements

### Requirement: El sistema SHALL separar contablemente en 3 segmentos (RN-35, RN-36, RN-38)
Las liquidaciones se segmentan en:
1. **General**: docentes sin excluir y que no son NEXO
2. **NEXO**: liquidaciones con es_nexo=true, se muestran separadas pero suman al total general
3. **Facturantes**: docentes con excluido_por_factura=true, NO generan pago directo en liquidación general

#### Scenario: Docente facturante excluido de liquidación general
- **WHEN** se calcula liquidación para un período
- **AND** un docente tiene excluido_por_factura=true
- **THEN** el sistema no genera Liquidacion para ese docente en el segmento general

#### Scenario: NEXO se marca separado
- **WHEN** un docente tiene rol NEXO y se calcula su liquidación
- **THEN** el sistema crea Liquidacion con es_nexo=true
- **AND** el monto se incluye en el total consolidado

#### Scenario: Vista consolidada muestra los 3 segmentos
- **WHEN** se consultan KPIs del período
- **THEN** el sistema retorna totales separados para general, NEXO y facturantes

### Requirement: El sistema SHALL exponer KPIs separados por segmento (RN-38)
Endpoint que retorna métricas agregadas del período: total general, total NEXO, total facturantes (abonadas y pendientes), cantidad de docentes por segmento.

#### Scenario: KPIs del período muestran montos y cantidades
- **WHEN** se envía GET /api/v1/liquidaciones/kpis?periodo=2026-06
- **AND** el usuario tiene permiso `liquidaciones:ver`
- **THEN** el sistema retorna 200 con:
  - total_general (suma liquidaciones donde es_nexo=false y excluido_por_factura=false)
  - total_nexo (suma liquidaciones donde es_nexo=true)
  - total_facturas_pendientes (suma facturas Pendientes del período)
  - total_facturas_abonadas (suma facturas Abonadas del período)
  - cantidad_docentes por segmento

#### Scenario: KPIs sin permiso retorna 403
- **WHEN** se envía GET /api/v1/liquidaciones/kpis sin permiso `liquidaciones:ver`
- **THEN** el sistema retorna 403
