"""Tests for asignacion vigencia (validity period).

Verifies that expired asignaciones return estado "Vencida"
and that the state is correctly derived from desde/hasta dates.
"""

import uuid
from datetime import datetime, timedelta, timezone

from app.models.asignacion import Asignacion


class TestAsignacionVigencia:
    def test_asignacion_vigente_dentro_del_rango(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now - timedelta(days=10),
            hasta=now + timedelta(days=10),
        )
        assert a.estado_vigencia == "Vigente"

    def test_asignacion_vencida_pasado_hasta(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now - timedelta(days=20),
            hasta=now - timedelta(days=1),
        )
        assert a.estado_vigencia == "Vencida"

    def test_asignacion_vigente_sin_hasta(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now - timedelta(days=5),
            hasta=None,
        )
        assert a.estado_vigencia == "Vigente"

    def test_asignacion_pendiente_futura(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now + timedelta(days=1),
            hasta=now + timedelta(days=30),
        )
        assert a.estado_vigencia == "Pendiente"

    def test_asignacion_exactamente_en_desde(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now,
            hasta=now + timedelta(days=10),
        )
        assert a.estado_vigencia == "Vigente"

    def test_asignacion_exactamente_en_hasta(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            desde=now - timedelta(days=10),
            hasta=now,
        )
        assert a.estado_vigencia == "Vencida"

    def test_vencida_no_otorga_permisos(self):
        now = datetime.now(timezone.utc)
        a = Asignacion(
            usuario_id=str(uuid.uuid4()),
            rol="PROFESOR",
            desde=now - timedelta(days=60),
            hasta=now - timedelta(days=1),
        )
        assert a.estado_vigencia == "Vencida"
        assert a.rol == "PROFESOR"
