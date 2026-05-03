"""
Tests unitarios aislados para los patrones de diseño de ArquiControl.

Estos tests verifican el comportamiento de Strategy, Factory Method, Observer,
Singleton y Repository SIN base de datos, SIN servidor y SIN requests HTTP.

Ejecutar desde la carpeta backend con el venv activado:
    pytest tests/test_design_patterns.py -v
"""

import pytest
from copy import deepcopy

from app.modules.proyectos.domain.strategies import (
    AvancePorFasesStrategy,
    AvancePorSeguimientosStrategy,
    AvanceStrategyResolver,
)
from app.modules.proyectos.domain.payment_factories import (
    AnticipoFactory,
    PagoGeneralFactory,
    PagoPorFaseFactory,
    PagoFactoryResolver,
)
from app.modules.proyectos.domain.observers import (
    AlertaPagosObserver,
    BitacoraProyectoObserver,
    IndicadoresProyectoObserver,
    ProyectoEventPublisher,
)
from app.modules.proyectos.domain.models import PagoCreate
from app.shared.catalogs import TipoPago
from app.core.database import MongoConnection


# ================================================================
# Fixtures: datos de prueba reutilizables
# ================================================================

@pytest.fixture
def proyecto_base():
    """Proyecto mínimo con datos suficientes para probar los patrones."""
    return {
        "id": "proy-test-001",
        "codigoProyecto": "TEST-001",
        "nombreProyecto": "Proyecto de prueba",
        "clienteId": "cli-test",
        "valorContrato": 100_000_000,
        "estadoProyecto": "EN_EJECUCION",
        "fechaFinEstimada": "2099-12-31",
        "porcentajeAvanceGeneral": 0,
        "fases": [
            {"id": "f1", "nombre": "Anteproyecto", "porcentajeAvance": 100, "isActive": True},
            {"id": "f2", "nombre": "Desarrollo", "porcentajeAvance": 60, "isActive": True},
            {"id": "f3", "nombre": "Ejecución", "porcentajeAvance": 20, "isActive": True},
        ],
        "seguimientos": [
            {"id": "s1", "faseId": "f1", "porcentajeAvance": 100, "isActive": True},
            {"id": "s2", "faseId": "f2", "porcentajeAvance": 50, "isActive": True},
            {"id": "s3", "faseId": "f2", "porcentajeAvance": 70, "isActive": True},
        ],
        "pagos": [],
        "contratistasAsignados": [],
        "compras": [],
        "documentos": [],
        "resumenFinanciero": {"saldoPendienteCliente": 0, "costoTotalEjecutado": 0},
        "bitacora": [],
        "alertas": [],
        "indicadores": {},
        "eventContext": {"target": "proyecto", "reason": None},
    }


@pytest.fixture
def pago_anticipo():
    """Payload de pago tipo ANTICIPO."""
    return PagoCreate(
        tipoPago=TipoPago.ANTICIPO,
        fechaPago="2026-04-01",
        monto=30_000_000,
        metodoPago="TRANSFERENCIA",
        referencia="TRX-TEST-001",
        concepto="Anticipo inicial de prueba",
        observaciones="Test unitario",
    )


@pytest.fixture
def pago_por_fase():
    """Payload de pago tipo PAGO_POR_FASE con faseId."""
    return PagoCreate(
        tipoPago=TipoPago.PAGO_POR_FASE,
        faseId="f2",
        fechaPago="2026-05-15",
        monto=20_000_000,
        metodoPago="TRANSFERENCIA",
        referencia="TRX-TEST-002",
        concepto="Pago por desarrollo técnico",
        observaciones="Test unitario",
    )


@pytest.fixture
def pago_general():
    """Payload de pago tipo PAGO_GENERAL."""
    return PagoCreate(
        tipoPago=TipoPago.PAGO_GENERAL,
        fechaPago="2026-06-01",
        monto=15_000_000,
        metodoPago="PSE",
        referencia="PSE-TEST-001",
        concepto="Pago general de avance",
        observaciones="Test unitario",
    )


# ================================================================
# 1. STRATEGY — Cálculo de avance general del proyecto
# ================================================================

class TestAvancePorSeguimientosStrategy:
    """Verifica que la estrategia de avance por seguimientos calcula
    el promedio de porcentajeAvance de los seguimientos activos."""

    def test_calcula_promedio_de_seguimientos_activos(self, proyecto_base):
        strategy = AvancePorSeguimientosStrategy()
        # seguimientos: 100, 50, 70 → promedio = 73.33
        resultado = strategy.calculate(proyecto_base)
        assert resultado == 73.33

    def test_ignora_seguimientos_inactivos(self, proyecto_base):
        strategy = AvancePorSeguimientosStrategy()
        proyecto_base["seguimientos"][2]["isActive"] = False
        # seguimientos activos: 100, 50 → promedio = 75.0
        resultado = strategy.calculate(proyecto_base)
        assert resultado == 75.0

    def test_retorna_cero_sin_seguimientos(self):
        strategy = AvancePorSeguimientosStrategy()
        resultado = strategy.calculate({"seguimientos": []})
        assert resultado == 0.0

    def test_retorna_cero_con_proyecto_vacio(self):
        strategy = AvancePorSeguimientosStrategy()
        resultado = strategy.calculate({})
        assert resultado == 0.0


class TestAvancePorFasesStrategy:
    """Verifica que la estrategia de avance por fases calcula
    el promedio de porcentajeAvance de las fases activas."""

    def test_calcula_promedio_de_fases_activas(self, proyecto_base):
        strategy = AvancePorFasesStrategy()
        # fases: 100, 60, 20 → promedio = 60.0
        resultado = strategy.calculate(proyecto_base)
        assert resultado == 60.0

    def test_ignora_fases_inactivas(self, proyecto_base):
        strategy = AvancePorFasesStrategy()
        proyecto_base["fases"][0]["isActive"] = False
        # fases activas: 60, 20 → promedio = 40.0
        resultado = strategy.calculate(proyecto_base)
        assert resultado == 40.0

    def test_retorna_cero_sin_fases(self):
        strategy = AvancePorFasesStrategy()
        resultado = strategy.calculate({"fases": []})
        assert resultado == 0.0


class TestAvanceStrategyResolver:
    """Verifica que el resolver devuelve la estrategia correcta
    según el método de cálculo solicitado."""

    def test_resuelve_estrategia_de_fases(self):
        resolver = AvanceStrategyResolver()
        strategy = resolver.resolve("FASES")
        assert isinstance(strategy, AvancePorFasesStrategy)

    def test_resuelve_estrategia_de_seguimientos(self):
        resolver = AvanceStrategyResolver()
        strategy = resolver.resolve("SEGUIMIENTOS")
        assert isinstance(strategy, AvancePorSeguimientosStrategy)

    def test_resuelve_seguimientos_por_defecto(self):
        resolver = AvanceStrategyResolver()
        strategy = resolver.resolve("CUALQUIER_COSA")
        assert isinstance(strategy, AvancePorSeguimientosStrategy)

    def test_estrategias_dan_resultados_distintos(self, proyecto_base):
        """Demuestra que la misma data da resultados distintos
        según la estrategia, justificando el uso del patrón."""
        resolver = AvanceStrategyResolver()
        avance_seguimientos = resolver.resolve("SEGUIMIENTOS").calculate(proyecto_base)
        avance_fases = resolver.resolve("FASES").calculate(proyecto_base)
        assert avance_seguimientos != avance_fases
        assert avance_seguimientos == 73.33  # promedio de 100, 50, 70
        assert avance_fases == 60.0          # promedio de 100, 60, 20


# ================================================================
# 2. FACTORY METHOD — Creación de pagos por tipo
# ================================================================

class TestAnticipoFactory:
    """Verifica que AnticipoFactory crea pagos con faseId nulo."""

    def test_crea_pago_con_id_generado(self, pago_anticipo):
        factory = AnticipoFactory()
        resultado = factory.create(pago_anticipo)
        assert "idPago" in resultado
        assert len(resultado["idPago"]) > 0

    def test_fuerza_fase_id_nulo(self, pago_anticipo):
        factory = AnticipoFactory()
        resultado = factory.create(pago_anticipo)
        assert resultado["faseId"] is None

    def test_conserva_monto_y_concepto(self, pago_anticipo):
        factory = AnticipoFactory()
        resultado = factory.create(pago_anticipo)
        assert resultado["monto"] == 30_000_000
        assert resultado["concepto"] == "Anticipo inicial de prueba"
        assert resultado["tipoPago"] == TipoPago.ANTICIPO


class TestPagoPorFaseFactory:
    """Verifica que PagoPorFaseFactory exige faseId y lo conserva."""

    def test_conserva_fase_id(self, pago_por_fase):
        factory = PagoPorFaseFactory()
        resultado = factory.create(pago_por_fase)
        assert resultado["faseId"] == "f2"

    def test_rechaza_pago_sin_fase_id(self):
        """La validación de faseId obligatorio se ejecuta en dos capas:
        1. El model_validator de PagoCreate rechaza la combinación PAGO_POR_FASE + faseId=None.
        2. La PagoPorFaseFactory valida lo mismo como segunda barrera.
        Este test verifica que al menos una de las dos capas impide la creación."""
        factory = PagoPorFaseFactory()
        with pytest.raises(Exception):
            pago_sin_fase = PagoCreate(
                tipoPago=TipoPago.PAGO_POR_FASE,
                faseId=None,
                fechaPago="2026-05-15",
                monto=20_000_000,
                metodoPago="TRANSFERENCIA",
                referencia="TRX-FAIL",
                concepto="Pago que debería fallar",
            )
            factory.create(pago_sin_fase)


class TestPagoGeneralFactory:
    """Verifica que PagoGeneralFactory crea pagos sin fase asociada."""

    def test_crea_pago_general_con_fase_nula(self, pago_general):
        factory = PagoGeneralFactory()
        resultado = factory.create(pago_general)
        assert resultado["faseId"] is None
        assert resultado["monto"] == 15_000_000


class TestPagoFactoryResolver:
    """Verifica que el resolver devuelve la factory correcta
    según el tipo de pago."""

    def test_resuelve_anticipo(self):
        resolver = PagoFactoryResolver()
        factory = resolver.resolve(TipoPago.ANTICIPO)
        assert isinstance(factory, AnticipoFactory)

    def test_resuelve_pago_por_fase(self):
        resolver = PagoFactoryResolver()
        factory = resolver.resolve(TipoPago.PAGO_POR_FASE)
        assert isinstance(factory, PagoPorFaseFactory)

    def test_resuelve_pago_general(self):
        resolver = PagoFactoryResolver()
        factory = resolver.resolve(TipoPago.PAGO_GENERAL)
        assert isinstance(factory, PagoGeneralFactory)

    def test_cada_tipo_genera_pagos_distintos(self, pago_anticipo, pago_por_fase, pago_general):
        """Demuestra que cada factory produce resultados con reglas distintas."""
        resolver = PagoFactoryResolver()
        anticipo = resolver.resolve(TipoPago.ANTICIPO).create(pago_anticipo)
        por_fase = resolver.resolve(TipoPago.PAGO_POR_FASE).create(pago_por_fase)
        general = resolver.resolve(TipoPago.PAGO_GENERAL).create(pago_general)
        # Anticipo y general fuerzan faseId a None
        assert anticipo["faseId"] is None
        assert general["faseId"] is None
        # Pago por fase conserva el faseId
        assert por_fase["faseId"] == "f2"
        # Los tres generan idPago distintos
        ids = {anticipo["idPago"], por_fase["idPago"], general["idPago"]}
        assert len(ids) == 3


# ================================================================
# 3. OBSERVER — Bitácora, indicadores y alertas
# ================================================================

class TestBitacoraProyectoObserver:
    """Verifica que el observer de bitácora registra eventos correctamente."""

    def test_agrega_evento_a_la_bitacora(self, proyecto_base):
        observer = BitacoraProyectoObserver()
        observer.handle("PROYECTO_CREADO", proyecto_base, "admin@test.com")
        assert len(proyecto_base["bitacora"]) == 1
        evento = proyecto_base["bitacora"][0]
        assert evento["evento"] == "PROYECTO_CREADO"
        assert evento["actor"] == "admin@test.com"
        assert "TEST-001" in evento["detalle"]

    def test_eventos_se_insertan_al_inicio(self, proyecto_base):
        observer = BitacoraProyectoObserver()
        observer.handle("EVENTO_1", proyecto_base, "usuario_a")
        observer.handle("EVENTO_2", proyecto_base, "usuario_b")
        assert proyecto_base["bitacora"][0]["evento"] == "EVENTO_2"
        assert proyecto_base["bitacora"][1]["evento"] == "EVENTO_1"

    def test_bitacora_no_excede_25_eventos(self, proyecto_base):
        observer = BitacoraProyectoObserver()
        for i in range(30):
            observer.handle(f"EVENTO_{i}", proyecto_base, "admin@test.com")
        assert len(proyecto_base["bitacora"]) == 25

    def test_incluye_motivo_cuando_se_proporciona(self, proyecto_base):
        observer = BitacoraProyectoObserver()
        proyecto_base["eventContext"] = {
            "target": "fase:f1",
            "reason": "Fase completada sin observaciones pendientes",
        }
        observer.handle("FASE_ELIMINADA", proyecto_base, "admin@test.com")
        evento = proyecto_base["bitacora"][0]
        assert "Motivo: Fase completada" in evento["detalle"]
        assert evento["motivo"] == "Fase completada sin observaciones pendientes"

    def test_registra_subregistro_tipo_e_id(self, proyecto_base):
        observer = BitacoraProyectoObserver()
        proyecto_base["eventContext"] = {"target": "pago:pag-001", "reason": None}
        observer.handle("PAGO_REGISTRADO", proyecto_base, "admin@test.com")
        evento = proyecto_base["bitacora"][0]
        assert evento["subregistroTipo"] == "pago"
        assert evento["subregistroId"] == "pag-001"


class TestIndicadoresProyectoObserver:
    """Verifica que el observer de indicadores calcula métricas correctamente."""

    def test_calcula_indicadores_basicos(self, proyecto_base):
        observer = IndicadoresProyectoObserver()
        observer.handle("PROYECTO_ACTUALIZADO", proyecto_base, "admin@test.com")
        indicadores = proyecto_base["indicadores"]
        assert indicadores["ultimoEvento"] == "PROYECTO_ACTUALIZADO"
        assert indicadores["actualizadoPor"] == "admin@test.com"
        assert indicadores["seguimientosRegistrados"] == 3
        assert indicadores["contratistasActivos"] == 0

    def test_cuenta_solo_contratistas_activos(self, proyecto_base):
        proyecto_base["contratistasAsignados"] = [
            {"estado": "ACTIVA", "isActive": True},
            {"estado": "ACTIVA", "isActive": False},
            {"estado": "SUSPENDIDA", "isActive": True},
            {"estado": "ACTIVA", "isActive": True},
        ]
        observer = IndicadoresProyectoObserver()
        observer.handle("TEST", proyecto_base, "admin@test.com")
        assert proyecto_base["indicadores"]["contratistasActivos"] == 2


class TestAlertaPagosObserver:
    """Verifica que el observer de alertas genera alertas
    cuando hay saldo pendiente alto o proyecto atrasado."""

    def test_genera_alerta_por_saldo_pendiente_alto(self, proyecto_base):
        # Saldo pendiente de 50M sobre contrato de 100M (50% > 10%)
        proyecto_base["resumenFinanciero"]["saldoPendienteCliente"] = 50_000_000
        observer = AlertaPagosObserver()
        observer.handle("PAGO_REGISTRADO", proyecto_base, "admin@test.com")
        alertas = proyecto_base["alertas"]
        assert len(alertas) >= 1
        alerta_pago = next(a for a in alertas if a["tipo"] == "ALERTA_PAGO")
        assert alerta_pago["nivel"] == "ALTO"

    def test_no_genera_alerta_con_saldo_bajo(self, proyecto_base):
        # Saldo pendiente de 5M sobre contrato de 100M (5% < 10%)
        proyecto_base["resumenFinanciero"]["saldoPendienteCliente"] = 5_000_000
        observer = AlertaPagosObserver()
        observer.handle("PAGO_REGISTRADO", proyecto_base, "admin@test.com")
        alertas_pago = [a for a in proyecto_base["alertas"] if a["tipo"] == "ALERTA_PAGO"]
        assert len(alertas_pago) == 0

    def test_genera_alerta_por_proyecto_atrasado(self, proyecto_base):
        proyecto_base["fechaFinEstimada"] = "2020-01-01"  # fecha ya pasada
        proyecto_base["estadoProyecto"] = "EN_EJECUCION"
        observer = AlertaPagosObserver()
        observer.handle("TEST", proyecto_base, "admin@test.com")
        alertas_atraso = [a for a in proyecto_base["alertas"] if a["tipo"] == "PROYECTO_ATRASADO"]
        assert len(alertas_atraso) == 1
        assert alertas_atraso[0]["nivel"] == "MEDIO"

    def test_no_genera_alerta_atraso_si_proyecto_finalizado(self, proyecto_base):
        proyecto_base["fechaFinEstimada"] = "2020-01-01"
        proyecto_base["estadoProyecto"] = "FINALIZADO"
        observer = AlertaPagosObserver()
        observer.handle("TEST", proyecto_base, "admin@test.com")
        alertas_atraso = [a for a in proyecto_base["alertas"] if a["tipo"] == "PROYECTO_ATRASADO"]
        assert len(alertas_atraso) == 0

    def test_limpia_event_context_despues_de_procesar(self, proyecto_base):
        observer = AlertaPagosObserver()
        observer.handle("TEST", proyecto_base, "admin@test.com")
        assert "eventContext" not in proyecto_base


class TestProyectoEventPublisher:
    """Verifica que el publisher notifica a TODOS los observers registrados."""

    def test_notifica_todos_los_observers(self, proyecto_base):
        publisher = ProyectoEventPublisher([
            BitacoraProyectoObserver(),
            IndicadoresProyectoObserver(),
            AlertaPagosObserver(),
        ])
        publisher.notify("PROYECTO_CREADO", proyecto_base, "admin@test.com")
        # Bitácora debe tener 1 evento
        assert len(proyecto_base["bitacora"]) == 1
        # Indicadores deben estar calculados
        assert proyecto_base["indicadores"]["ultimoEvento"] == "PROYECTO_CREADO"
        # Alertas deben haberse evaluado (vacías porque no hay saldo pendiente)
        assert isinstance(proyecto_base["alertas"], list)

    def test_publisher_sin_observers_no_falla(self, proyecto_base):
        publisher = ProyectoEventPublisher([])
        publisher.notify("TEST", proyecto_base, "admin@test.com")
        # No debe lanzar excepción


# ================================================================
# 4. SINGLETON — Conexión a MongoDB
# ================================================================

class TestMongoConnectionSingleton:
    """Verifica que MongoConnection siempre devuelve la misma instancia."""

    def test_misma_instancia_en_multiples_llamadas(self):
        instancia_1 = MongoConnection()
        instancia_2 = MongoConnection()
        assert instancia_1 is instancia_2

    def test_misma_base_de_datos(self):
        instancia_1 = MongoConnection()
        instancia_2 = MongoConnection()
        assert instancia_1.database is instancia_2.database


# ================================================================
# 5. REPOSITORY — Interfaz abstracta
# ================================================================

class TestRepositoryInterface:
    """Verifica que las interfaces de repositorio están correctamente
    definidas como clases abstractas y no pueden instanciarse."""

    def test_no_se_puede_instanciar_repositorio_abstracto(self):
        from app.modules.proyectos.domain.repositories import IProyectoRepository
        with pytest.raises(TypeError):
            IProyectoRepository()

    def test_no_se_puede_instanciar_cliente_repositorio_abstracto(self):
        from app.modules.clientes.domain.repositories import IClienteRepository
        with pytest.raises(TypeError):
            IClienteRepository()

    def test_implementacion_concreta_hereda_de_interfaz(self):
        from app.modules.proyectos.domain.repositories import IProyectoRepository
        from app.modules.proyectos.infrastructure.repository import ProyectoRepository
        assert issubclass(ProyectoRepository, IProyectoRepository)

    def test_implementacion_clientes_hereda_de_interfaz(self):
        from app.modules.clientes.domain.repositories import IClienteRepository
        from app.modules.clientes.infrastructure.repository import ClienteRepository
        assert issubclass(ClienteRepository, IClienteRepository)