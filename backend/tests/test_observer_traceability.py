import os
from datetime import datetime

import pytest
import requests


# Observer + bitácora + logical delete traceability validations
BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")


@pytest.fixture(scope="session")
def api_base_url() -> str:
    assert BASE_URL, "REACT_APP_BACKEND_URL is required for public endpoint testing"
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def api_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture(scope="session")
def auth_context(api_client: requests.Session, api_base_url: str) -> dict:
    login = api_client.post(
        f"{api_base_url}/api/auth/login",
        json={
            "email": "admin@arquicontrol.com",
            "password": "ArquiControl2026!",
        },
        timeout=30,
    )
    assert login.status_code == 200, login.text
    data = login.json()
    token = data.get("token")
    assert isinstance(token, str) and token
    api_client.headers.update({"Authorization": f"Bearer {token}"})
    return data


@pytest.fixture
def project_id(api_client: requests.Session, api_base_url: str, auth_context: dict) -> str:
    del auth_context
    response = api_client.get(f"{api_base_url}/api/proyectos", timeout=30)
    assert response.status_code == 200, response.text
    projects = response.json()
    assert isinstance(projects, list) and len(projects) > 0
    return projects[0]["id"]


class TestObserverAndTraceability:
    def test_project_has_observer_fields(self, api_client: requests.Session, api_base_url: str, project_id: str):
        response = api_client.get(f"{api_base_url}/api/proyectos/{project_id}", timeout=30)
        assert response.status_code == 200, response.text
        project = response.json()

        assert isinstance(project.get("bitacora"), list)
        assert isinstance(project.get("alertas"), list)
        assert isinstance(project.get("indicadores"), dict)

    def test_payment_mutation_updates_bitacora_indicators_and_feed_exclusion(
        self,
        api_client: requests.Session,
        api_base_url: str,
        project_id: str,
    ):
        payment_payload = {
            "tipoPago": "PAGO_GENERAL",
            "faseId": None,
            "fechaPago": datetime.utcnow().strftime("%Y-%m-%d"),
            "monto": 777,
            "metodoPago": "TRANSFERENCIA",
            "referencia": "TEST-OBS-TRACE",
            "concepto": "TEST observer traceability",
            "observaciones": "test",
        }
        create_response = api_client.post(
            f"{api_base_url}/api/proyectos/{project_id}/pagos",
            json=payment_payload,
            timeout=30,
        )
        assert create_response.status_code == 200, create_response.text
        created_project = create_response.json()

        created_payment_id = created_project["pagos"][0]["idPago"]
        assert created_project["bitacora"][0]["evento"] == "PAGO_REGISTRADO"
        assert created_project["indicadores"]["ultimoEvento"] == "PAGO_REGISTRADO"

        invalid_delete_response = api_client.delete(
            f"{api_base_url}/api/proyectos/{project_id}/pagos/{created_payment_id}",
            json={"motivo": "   "},
            timeout=30,
        )
        assert invalid_delete_response.status_code == 422, invalid_delete_response.text

        reason = "TEST eliminación lógica observador"
        delete_response = api_client.delete(
            f"{api_base_url}/api/proyectos/{project_id}/pagos/{created_payment_id}",
            json={"motivo": reason},
            timeout=30,
        )
        assert delete_response.status_code == 200, delete_response.text
        deleted_project = delete_response.json()

        assert all(payment["idPago"] != created_payment_id for payment in deleted_project["pagos"])
        assert deleted_project["bitacora"][0]["evento"] == "PAGO_ELIMINADO_LOGICAMENTE"
        assert reason in deleted_project["bitacora"][0]["detalle"]
        assert deleted_project["indicadores"]["ultimoEvento"] == "PAGO_ELIMINADO_LOGICAMENTE"

        payments_feed_response = api_client.get(f"{api_base_url}/api/pagos", timeout=30)
        assert payments_feed_response.status_code == 200, payments_feed_response.text
        feed = payments_feed_response.json()
        assert all(item.get("payment", {}).get("idPago") != created_payment_id for item in feed)

    def test_bitacora_global_and_report_exports(self, api_client: requests.Session, api_base_url: str, project_id: str):
        bitacora_response = api_client.get(
            f"{api_base_url}/api/bitacora",
            params={"proyectoId": project_id},
            timeout=30,
        )
        assert bitacora_response.status_code == 200, bitacora_response.text
        bitacora = bitacora_response.json()
        assert isinstance(bitacora, list)
        if bitacora:
            assert all(item.get("projectId") == project_id for item in bitacora)
            assert all(item.get("codigoProyecto") for item in bitacora)

        pdf_response = api_client.get(f"{api_base_url}/api/proyectos/{project_id}/reportes/resumen-cliente.pdf", timeout=30)
        assert pdf_response.status_code == 200, pdf_response.text
        assert pdf_response.headers["content-type"].startswith("application/pdf")
        assert pdf_response.content.startswith(b"%PDF")

        financial_csv_response = api_client.get(f"{api_base_url}/api/proyectos/{project_id}/reportes/pagos-compras.csv", timeout=30)
        assert financial_csv_response.status_code == 200, financial_csv_response.text
        assert "text/csv" in financial_csv_response.headers["content-type"]
        assert "categoria,codigoProyecto,proyecto" in financial_csv_response.text

        contractors_csv_response = api_client.get(f"{api_base_url}/api/proyectos/{project_id}/reportes/contratistas.csv", timeout=30)
        assert contractors_csv_response.status_code == 200, contractors_csv_response.text
        assert "text/csv" in contractors_csv_response.headers["content-type"]
        assert "codigoProyecto,proyecto,contratista" in contractors_csv_response.text
