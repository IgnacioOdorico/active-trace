from app.core.seed import SEED_ROLES, PERMISO_DESCRIPTIONS


class TestSeedPermissions:
    def test_nuevos_permisos_en_descriptions(self):
        assert "liquidaciones:calcular" in PERMISO_DESCRIPTIONS
        assert "liquidaciones:cerrar" in PERMISO_DESCRIPTIONS
        assert "liquidaciones:exportar" in PERMISO_DESCRIPTIONS
        assert "liquidaciones:configurar-salarios" in PERMISO_DESCRIPTIONS
        assert "facturas:cargar" in PERMISO_DESCRIPTIONS
        assert "facturas:abonar" in PERMISO_DESCRIPTIONS

    def test_finanzas_tiene_wildcards(self):
        finanzas = SEED_ROLES.get("FINANZAS", [])
        assert "liquidaciones:*" in finanzas
        assert "facturas:*" in finanzas

    def test_nexo_tiene_lectura(self):
        nexo = SEED_ROLES.get("NEXO", [])
        assert "liquidaciones:ver" in nexo
        assert "facturas:ver" in nexo
