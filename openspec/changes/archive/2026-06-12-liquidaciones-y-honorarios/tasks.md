## 1. Modelos y migración

- [x] 1.1 Crear `models/salario_base.py`: SalarioBase con id, tenant_id, rol (PROFESOR|TUTOR|NEXO|COORDINADOR|ALL), monto, desde, hasta nullable
- [x] 1.2 Crear `models/salario_plus.py`: SalarioPlus con id, tenant_id, grupo, rol, descripcion, monto, desde, hasta nullable
- [x] 1.3 Crear `models/liquidacion.py`: Liquidacion con id, tenant_id, cohorte_id, periodo, usuario_id, rol, comisiones(lista texto), monto_base, monto_plus, total, es_nexo, excluido_por_factura, estado (Abierta|Cerrada)
- [x] 1.4 Crear `models/factura.py`: Factura con id, tenant_id, usuario_id, periodo, detalle, referencia_archivo, tamano_kb, estado (Pendiente|Abonada), cargada_at, abonada_at nullable
- [x] 1.5 Registrar los 4 modelos en `models/__init__.py` con exports
- [x] 1.6 (RED→GREEN) Tests de atributos de modelo (51 tests pasan sin DB)
- [x] 1.7 Generar migration Alembic con las 4 tablas
- [x] 1.8 (GREEN) Ejecutar migration contra DB de test

## 2. Esquemas Pydantic v2

- [x] 2.1 Crear `schemas/salario_base.py`: SalarioBaseCreate, SalarioBaseUpdate, SalarioBaseResponse
- [x] 2.2 Crear `schemas/salario_plus.py`: SalarioPlusCreate, SalarioPlusUpdate, SalarioPlusResponse
- [x] 2.3 Crear `schemas/liquidacion.py`: LiquidacionResponse, LiquidacionListResponse, LiquidacionKPI, CalcularLiquidacionRequest
- [x] 2.4 Crear `schemas/factura.py`: FacturaResponse, FacturaAbonar

## 3. Repositorios (tenant-scoped)

- [x] 3.1 Implementar `repositories/salario_base.py`: CRUD con validación de solapamiento temporal
- [x] 3.2 Implementar `repositories/salario_plus.py`: CRUD con validación de solapamiento temporal
- [x] 3.3 Implementar `repositories/liquidacion.py`: listar por período y cohorte, cerrar, KPIs
- [x] 3.4 Implementar `repositories/factura.py`: crear, listar por período/estado, abonar

## 4. Servicio de cálculo de liquidación (RN-34)

- [x] 4.1 (RED→GREEN) Tests del cálculo de liquidación: 8 tests con mock (periodo cerrado, sin comisiones, cerrar OK, cerrar ya cerrada, listar, KPIs)
- [x] 4.2 (RED→GREEN) Test de RN-22: recalcular período cerrado retorna DomainError
- [x] 4.3 (GREEN) Implementar `services/liquidaciones.py`: `calcular_liquidacion(cohorte_id, periodo)` con lógica RN-34 completa
- [x] 4.4 (TRIANGULATE) Casos NEXO (es_nexo=true) y facturante (excluido_por_factura según User.facturador)

## 5. Endpoints REST

- [x] 5.1 Implementar `routers/salario_base.py`: CRUD con permiso `liquidaciones:configurar-salarios`, audit SALARIO_CONFIGURAR
- [x] 5.2 Implementar `routers/salario_plus.py`: CRUD con permiso `liquidaciones:configurar-salarios`, audit SALARIO_CONFIGURAR
- [x] 5.3 Implementar `routers/liquidaciones.py`: GET listar, POST calcular, POST cerrar, GET historial, GET kpis
- [x] 5.4 Implementar `routers/facturas.py`: POST con upload PDF, PATCH abonar, GET listar
- [x] 5.5 (RED→GREEN) Tests de endpoints con mock (calcular OK, 409, cerrar OK, 409, listar, KPIs)
- [x] 5.6 (GREEN) Todos los tests de endpoints pasan

## 6. File upload para facturas

- [x] 6.1 Configurar FACTURAS_DIR y MAX_FILE_SIZE_KB en Settings
- [x] 6.2 Implementar helper save_factura_pdf en router facturas.py
- [x] 6.3 Validar tipo PDF (por extensión) y tamaño máximo
- [x] 6.4 (RED→GREEN) Tests de validación en facturas router
- [x] 6.5 Validación y almacenamiento implementados

## 7. Permisos y seed

- [x] 7.1 Agregados 6 nuevos permisos en seed.py + PERMISO_DESCRIPTIONS
- [x] 7.2 SEED_ROLES actualizado: FINANZAS ya tiene wildcards; NEXO tiene lectura
- [x] 7.3 Descripciones de permisos agregadas
- [x] 7.4 (RED→GREEN) Tests de seed verifican nuevos permisos
- [x] 7.5 Seed actualizado con todos los permisos

## 8. Auditoría

- [x] 8.1 Audit actions agregadas: LIQUIDACION_CALCULAR, LIQUIDACION_CERRAR, FACTURA_CARGAR, FACTURA_ABONAR, SALARIO_CONFIGURAR
- [x] 8.2 (RED→GREEN) Tests de audit verifican constantes y servicio
- [x] 8.3 Audit inyectado en cada endpoint (salario_base, salario_plus, liquidaciones, facturas)

## 9. Validación de inmutabilidad

- [x] 9.1 Implementado `_validar_no_cerrada(id)` en LiquidacionRepository
- [x] 9.2 (RED→GREEN) Tests: modificar/cerrar liquidación cerrada retorna DomainError
- [x] 9.3 Validación implementada en repo y service layer

## 10. Verificación final

- [x] 10.1 Suite completa: **925 passed, 94 skipped (DB-dependent), 0 failures**
- [x] 10.2 Cada endpoint requiere el permiso correcto (liquidaciones:* y facturas:*)
- [x] 10.3 Audit registrado en cada acción financiera
- [x] 10.4 Ningún archivo supera 500 LOC (máximo: services/liquidaciones.py = 203 LOC)
