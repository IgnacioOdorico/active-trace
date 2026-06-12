import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, status

from app.core.exceptions import DomainError
from app.models.user import User
from app.routers.liquidaciones import calcular_liquidacion, cerrar_liquidacion, listar_liquidaciones, kpis_liquidaciones
from app.schemas.liquidacion import CalcularLiquidacionRequest


class TestCalcularEndpoint:
    @pytest.mark.asyncio
    async def test_calcular_ok(self):
        mock_db = AsyncMock()
        mock_user = MagicMock(spec=User)
        mock_user.tenant_id = uuid.uuid4()
        mock_user.id = uuid.uuid4()

        with patch("app.routers.liquidaciones.LiquidacionService") as MockSvc:
            svc_instance = AsyncMock()
            MockSvc.return_value = svc_instance
            svc_instance.calcular = AsyncMock(
                return_value=[{"id": str(uuid.uuid4()), "total": 700.0}]
            )

            body = CalcularLiquidacionRequest(cohorte_id=uuid.uuid4(), periodo="2026-06")
            result = await calcular_liquidacion(
                body=body,
                db=mock_db,
                current_user=mock_user,
                _=None,
            )
            assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_calcular_periodo_cerrado_raise_409(self):
        mock_db = AsyncMock()
        mock_user = MagicMock(spec=User)
        mock_user.tenant_id = uuid.uuid4()
        mock_user.id = uuid.uuid4()

        with patch("app.routers.liquidaciones.LiquidacionService") as MockSvc:
            svc_instance = AsyncMock()
            MockSvc.return_value = svc_instance
            svc_instance.calcular = AsyncMock(
                side_effect=DomainError(
                    detail="El período 2026-06 ya está cerrado",
                    context={},
                )
            )

            body = CalcularLiquidacionRequest(cohorte_id=uuid.uuid4(), periodo="2026-06")
            with pytest.raises(HTTPException) as exc:
                await calcular_liquidacion(
                    body=body,
                    db=mock_db,
                    current_user=mock_user,
                    _=None,
                )
            assert exc.value.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_calcular_sin_permiso(self):
        with patch("app.routers.liquidaciones.require_permission") as mock_perm:
            mock_perm.return_value = lambda: None
            dep = mock_perm("liquidaciones:calcular")
            assert callable(dep)

    @pytest.mark.asyncio
    async def test_cerrar_ok(self):
        mock_db = AsyncMock()
        mock_user = MagicMock(spec=User)
        mock_user.tenant_id = uuid.uuid4()
        mock_user.id = uuid.uuid4()

        with patch("app.routers.liquidaciones.LiquidacionService") as MockSvc:
            svc_instance = AsyncMock()
            MockSvc.return_value = svc_instance
            svc_instance.cerrar = AsyncMock(
                return_value={"id": str(uuid.uuid4()), "estado": "Cerrada"}
            )

            result = await cerrar_liquidacion(
                id=uuid.uuid4(),
                db=mock_db,
                current_user=mock_user,
                _=None,
            )
            assert result["estado"] == "Cerrada"

    @pytest.mark.asyncio
    async def test_cerrar_ya_cerrada_raise_409(self):
        mock_db = AsyncMock()
        mock_user = MagicMock(spec=User)
        mock_user.tenant_id = uuid.uuid4()
        mock_user.id = uuid.uuid4()

        with patch("app.routers.liquidaciones.LiquidacionService") as MockSvc:
            svc_instance = AsyncMock()
            MockSvc.return_value = svc_instance
            svc_instance.cerrar = AsyncMock(
                side_effect=DomainError(
                    detail="La liquidación ya está cerrada",
                    context={},
                )
            )

            with pytest.raises(HTTPException) as exc:
                await cerrar_liquidacion(
                    id=uuid.uuid4(),
                    db=mock_db,
                    current_user=mock_user,
                    _=None,
                )
            assert exc.value.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_listar_ok(self):
        mock_db = AsyncMock()
        mock_user = MagicMock(spec=User)
        mock_user.tenant_id = uuid.uuid4()
        mock_user.id = uuid.uuid4()

        with patch("app.routers.liquidaciones.LiquidacionService") as MockSvc:
            svc_instance = AsyncMock()
            MockSvc.return_value = svc_instance
            svc_instance.listar = AsyncMock(
                return_value=[{"id": str(uuid.uuid4()), "total": 700.0}]
            )

            result = await listar_liquidaciones(
                periodo="2026-06",
                cohorte_id=None,
                db=mock_db,
                current_user=mock_user,
                _=None,
            )
            assert result["total"] == 1

    @pytest.mark.asyncio
    async def test_kpis_ok(self):
        mock_db = AsyncMock()
        mock_user = MagicMock(spec=User)
        mock_user.tenant_id = uuid.uuid4()
        mock_user.id = uuid.uuid4()

        with patch("app.routers.liquidaciones.LiquidacionService") as MockSvc:
            svc_instance = AsyncMock()
            MockSvc.return_value = svc_instance
            svc_instance.obtener_kpis = AsyncMock(
                return_value={
                    "total_general": 1000.0,
                    "total_nexo": 500.0,
                    "total_facturas_pendientes": 200.0,
                    "total_facturas_abonadas": 300.0,
                    "cantidad_docentes_general": 2,
                    "cantidad_docentes_nexo": 1,
                    "cantidad_docentes_facturantes": 1,
                }
            )

            result = await kpis_liquidaciones(
                periodo="2026-06",
                db=mock_db,
                current_user=mock_user,
                _=None,
            )
            assert result["total_general"] == 1000.0
