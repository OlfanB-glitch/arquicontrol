import os
from datetime import datetime

import pytest
import requests


# Core API auth and seeded catalog coverage
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
    response = api_client.post(
        f"{api_base_url}/api/auth/login",
        json={
            "email": "admin@arquicontrol.com",
            "password": "ArquiControl2026!",
        },
        timeout=30,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data.get("token"), str) and data["token"]
    assert data.get("user", {}).get("email") == "admin@arquicontrol.com"

    token = data["token"]
    api_client.headers.update({"Authorization": f"Bearer {token}"})
    return {"token": token, "user": data["user"]}


@pytest.fixture(scope="session")
def seeded_data(api_client: requests.Session, api_base_url: str, auth_context: dict) -> dict:
    del auth_context

    clientes = api_client.get(f"{api_base_url}/api/clientes", timeout=30)
    contratistas = api_client.get(f"{api_base_url}/api/contratistas", timeout=30)
    proveedores = api_client.get(f"{api_base_url}/api/proveedores", timeout=30)
    materiales = api_client.get(f"{api_base_url}/api/materiales", timeout=30)
    proyectos = api_client.get(f"{api_base_url}/api/proyectos", timeout=30)

    for response in [clientes, contratistas, proveedores, materiales, proyectos]:
        assert response.status_code == 200, response.text
        assert isinstance(response.json(), list)

    clientes_data = clientes.json()
    contratistas_data = contratistas.json()
    proveedores_data = proveedores.json()
    materiales_data = materiales.json()
    proyectos_data = proyectos.json()

    assert len(clientes_data) > 0
    assert len(contratistas_data) > 0
    assert len(proveedores_data) > 0
    assert len(materiales_data) > 0
    assert len(proyectos_data) > 0

    return {
        "cliente_id": clientes_data[0]["id"],
        "contratista_id": contratistas_data[0]["id"],
        "proveedor_id": proveedores_data[0]["id"],
        "material_id": materiales_data[0]["id"],
        "project_id": proyectos_data[0]["id"],
    }


@pytest.fixture(scope="session")
def workflow_state() -> dict:
    return {
        "assignment_id": None,
        "tracking_id": None,
        "payment_id": None,
        "purchase_id": None,
        "document_id": None,
        "uploaded_document_id": None,
        "temp_phase_id": None,
        "temp_assignment_id": None,
        "delete_payment_id": None,
        "delete_purchase_id": None,
    }


class TestArquicontrolCore:
    # Authentication and dashboard summary validations
    def test_01_login_and_me(self, api_client: requests.Session, api_base_url: str, auth_context: dict):
        assert auth_context["user"]["rol"]
        me_response = api_client.get(f"{api_base_url}/api/auth/me", timeout=30)
        assert me_response.status_code == 200, me_response.text
        me_data = me_response.json()
        assert me_data["email"] == "admin@arquicontrol.com"
        assert isinstance(me_data["id"], str)

    def test_02_dashboard_summary_structure(
        self,
        api_client: requests.Session,
        api_base_url: str,
        auth_context: dict,
    ):
        del auth_context
        response = api_client.get(f"{api_base_url}/api/dashboard/summary", timeout=30)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data.get("totalClientes"), int)
        assert isinstance(data.get("totalProyectos"), int)
        assert isinstance(data.get("proyectosPorEstado"), dict)
        assert isinstance(data.get("pagosRecientes"), list)
        assert isinstance(data.get("comprasRecientes"), list)
        assert isinstance(data.get("eventosRecientes"), list)

    # Seeded entities and project list coverage
    def test_03_seeded_catalog_endpoints(self, seeded_data: dict):
        assert isinstance(seeded_data["cliente_id"], str)
        assert isinstance(seeded_data["contratista_id"], str)
        assert isinstance(seeded_data["proveedor_id"], str)
        assert isinstance(seeded_data["material_id"], str)

    def test_04_project_detail_load(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
    ):
        response = api_client.get(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}", timeout=30)
        assert response.status_code == 200, response.text
        project = response.json()
        assert project["id"] == seeded_data["project_id"]
        assert isinstance(project.get("fases"), list)
        assert len(project["fases"]) > 0

    # Main project detail workflow coverage: tracking, payments, assignments, purchases, docs
    def test_05_register_tracking(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        project_response = api_client.get(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}", timeout=30)
        assert project_response.status_code == 200, project_response.text
        project = project_response.json()
        fase_id = project["fases"][0]["id"]

        payload = {
            "faseId": fase_id,
            "fecha": datetime.utcnow().strftime("%Y-%m-%d"),
            "observaciones": "TEST seguimiento API",
            "porcentajeAvance": 35,
            "evidencias": [
                {
                    "nombre": "TEST evidencia",
                    "url": "https://example.com/evidencia-test",
                    "descripcion": "Evidencia de prueba",
                },
            ],
        }
        response = api_client.post(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/seguimientos", json=payload, timeout=30)
        assert response.status_code == 200, response.text
        updated = response.json()
        assert len(updated.get("seguimientos", [])) > 0
        workflow_state["tracking_id"] = updated["seguimientos"][0]["id"]
        assert updated["seguimientos"][0]["observaciones"] == "TEST seguimiento API"

    def test_06_register_client_payment(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        payload = {
            "tipoPago": "PAGO_GENERAL",
            "faseId": None,
            "fechaPago": datetime.utcnow().strftime("%Y-%m-%d"),
            "monto": 1500,
            "metodoPago": "TRANSFERENCIA",
            "referencia": "TEST-REF-PAGO",
            "concepto": "TEST pago general cliente",
            "observaciones": "Pago API test",
        }
        response = api_client.post(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/pagos", json=payload, timeout=30)
        assert response.status_code == 200, response.text
        updated = response.json()
        assert len(updated.get("pagos", [])) > 0
        workflow_state["payment_id"] = updated["pagos"][0]["idPago"]
        assert float(updated["pagos"][0]["monto"]) == 1500

    def test_07_assign_contractor(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        payload = {
            "contratistaId": seeded_data["contratista_id"],
            "rol": "TEST Supervisor Obra",
            "fechaInicio": datetime.utcnow().strftime("%Y-%m-%d"),
            "fechaFin": None,
            "valorAcordado": 900,
            "estado": "ACTIVA",
        }
        response = api_client.post(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/contratistas", json=payload, timeout=30)
        assert response.status_code == 200, response.text
        updated = response.json()
        assert len(updated.get("contratistasAsignados", [])) > 0
        assignment = updated["contratistasAsignados"][0]
        workflow_state["assignment_id"] = assignment["idAsignacion"]
        assert assignment["contratistaId"] == seeded_data["contratista_id"]

    def test_08_register_contractor_progress(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        assert workflow_state["assignment_id"], "assignment_id missing from previous step"
        payload = {
            "fecha": datetime.utcnow().strftime("%Y-%m-%d"),
            "descripcion": "TEST avance contratista",
            "jornadaHoras": 8,
            "porcentajeAvance": 12,
        }
        response = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/contratistas/{workflow_state['assignment_id']}/avances",
            json=payload,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        updated = response.json()
        assignment = next(item for item in updated["contratistasAsignados"] if item["idAsignacion"] == workflow_state["assignment_id"])
        assert len(assignment.get("avances", [])) > 0
        assert assignment["avances"][0]["descripcion"] == "TEST avance contratista"

    def test_09_register_contractor_payment(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        assert workflow_state["assignment_id"], "assignment_id missing from previous step"
        payload = {
            "fechaPago": datetime.utcnow().strftime("%Y-%m-%d"),
            "monto": 300,
            "referencia": "TEST-REF-CONTR",
            "observaciones": "TEST pago contratista",
        }
        response = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/contratistas/{workflow_state['assignment_id']}/pagos",
            json=payload,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        updated = response.json()
        assignment = next(item for item in updated["contratistasAsignados"] if item["idAsignacion"] == workflow_state["assignment_id"])
        assert len(assignment.get("pagosContratista", [])) > 0
        assert float(assignment["pagosContratista"][0]["monto"]) == 300

    def test_10_register_purchase(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        payload = {
            "proveedorId": seeded_data["proveedor_id"],
            "fechaCompra": datetime.utcnow().strftime("%Y-%m-%d"),
            "numeroFactura": f"TEST-FAC-{datetime.utcnow().strftime('%H%M%S')}",
            "impuesto": 19,
            "observaciones": "TEST compra API",
            "detalleCompra": [
                {
                    "materialId": seeded_data["material_id"],
                    "cantidad": 2,
                    "precioUnitario": 125,
                },
            ],
        }
        response = api_client.post(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/compras", json=payload, timeout=30)
        assert response.status_code == 200, response.text
        updated = response.json()
        assert len(updated.get("compras", [])) > 0
        purchase = updated["compras"][0]
        workflow_state["purchase_id"] = purchase["idCompra"]
        assert purchase["proveedorId"] == seeded_data["proveedor_id"]
        assert len(purchase.get("detalleCompra", [])) == 1

    def test_11_register_document_url(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        payload = {
            "nombre": "TEST Documento URL",
            "url": "https://example.com/planos-test",
            "tipo": "DOCUMENTO",
            "seguimientoId": None,
            "observaciones": "TEST documento URL",
        }
        response = api_client.post(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/documentos/url", json=payload, timeout=30)
        assert response.status_code == 200, response.text
        updated = response.json()
        assert len(updated.get("documentos", [])) > 0
        document = updated["documentos"][0]
        workflow_state["document_id"] = document["id"]
        assert document["nombre"] == "TEST Documento URL"
        assert document["fuente"] == "URL"

    def test_12_upload_document_file(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        data = {
            "tipo": "EVIDENCIA",
            "seguimientoId": "",
            "observaciones": "TEST archivo subido",
        }
        files = {
            "file": ("test-evidencia.txt", b"archivo prueba arquicontrol", "text/plain"),
        }
        # Remove JSON content-type to allow multipart
        api_client.headers.pop("Content-Type", None)
        response = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/documentos/upload",
            data=data,
            files=files,
            timeout=30,
        )
        api_client.headers.update({"Content-Type": "application/json"})

        assert response.status_code == 200, response.text
        updated = response.json()
        assert len(updated.get("documentos", [])) > 0
        file_doc = updated["documentos"][0]
        workflow_state["uploaded_document_id"] = file_doc["id"]
        assert file_doc["fuente"] == "ARCHIVO"
        assert file_doc["url"].startswith("/api/files/")

    # Added pages/endpoints coverage and persisted model checks
    def test_13_pagos_feed(
        self,
        api_client: requests.Session,
        api_base_url: str,
        workflow_state: dict,
    ):
        response = api_client.get(f"{api_base_url}/api/pagos", timeout=30)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert any(item.get("payment", {}).get("idPago") == workflow_state["payment_id"] for item in data)

    def test_14_compras_feed(
        self,
        api_client: requests.Session,
        api_base_url: str,
        workflow_state: dict,
    ):
        response = api_client.get(f"{api_base_url}/api/compras", timeout=30)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert any(item.get("purchase", {}).get("idCompra") == workflow_state["purchase_id"] for item in data)

    def test_15_documentos_feed(
        self,
        api_client: requests.Session,
        api_base_url: str,
        workflow_state: dict,
    ):
        response = api_client.get(f"{api_base_url}/api/documentos", timeout=30)
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        document_ids = [item.get("document", {}).get("id") for item in data]
        assert workflow_state["document_id"] in document_ids
        assert workflow_state["uploaded_document_id"] in document_ids

    def test_16_update_individual_embedded_records(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        project_response = api_client.get(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}", timeout=30)
        assert project_response.status_code == 200, project_response.text
        project = project_response.json()

        project_update_payload = {
            "codigoProyecto": project["codigoProyecto"],
            "clienteId": project["clienteId"],
            "nombreProyecto": project["nombreProyecto"],
            "tipoProyecto": project["tipoProyecto"],
            "descripcion": project["descripcion"],
            "ubicacion": project["ubicacion"],
            "area": project["area"],
            "presupuestoEstimado": project["presupuestoEstimado"],
            "valorContrato": project["valorContrato"],
            "estadoProyecto": project["estadoProyecto"],
            "fechaInicio": project["fechaInicio"],
            "fechaFinEstimada": project["fechaFinEstimada"],
            "porcentajeAvanceGeneral": project["porcentajeAvanceGeneral"],
            "observacionesGenerales": project["observacionesGenerales"],
            "metodoCalculoAvance": project.get("metodoCalculoAvance", "SEGUIMIENTOS"),
            "fases": [
                {
                    "nombre": fase["nombre"],
                    "descripcion": fase.get("descripcion", ""),
                    "porcentajePlaneado": fase.get("porcentajePlaneado", 0),
                    "porcentajeAvance": fase.get("porcentajeAvance", 0),
                    "fechaInicio": fase.get("fechaInicio"),
                    "fechaFinEstimada": fase.get("fechaFinEstimada"),
                    "estado": fase.get("estado", "PENDIENTE"),
                }
                for fase in project["fases"]
            ]
            + [
                {
                    "nombre": "TEST fase temporal",
                    "descripcion": "Fase temporal para prueba de eliminación lógica",
                    "porcentajePlaneado": 5,
                    "porcentajeAvance": 0,
                    "fechaInicio": project["fechaInicio"],
                    "fechaFinEstimada": project["fechaFinEstimada"],
                    "estado": "PENDIENTE",
                },
            ],
        }
        update_project_response = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}",
            json=project_update_payload,
            timeout=30,
        )
        assert update_project_response.status_code == 200, update_project_response.text
        updated_project = update_project_response.json()
        temp_phase = next(item for item in updated_project["fases"] if item["nombre"] == "TEST fase temporal")
        workflow_state["temp_phase_id"] = temp_phase["id"]

        phase_update = {
            "nombre": "TEST fase temporal editada",
            "descripcion": "Fase temporal actualizada",
            "porcentajePlaneado": 7,
            "porcentajeAvance": 3,
            "fechaInicio": project["fechaInicio"],
            "fechaFinEstimada": project["fechaFinEstimada"],
            "estado": "EN_PROCESO",
        }
        response = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/fases/{workflow_state['temp_phase_id']}",
            json=phase_update,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        phase = next(item for item in response.json()["fases"] if item["id"] == workflow_state["temp_phase_id"])
        assert phase["nombre"] == "TEST fase temporal editada"

        tracking_update = {
            "faseId": project["fases"][0]["id"],
            "fecha": datetime.utcnow().strftime("%Y-%m-%d"),
            "observaciones": "TEST seguimiento editado",
            "porcentajeAvance": 48,
            "evidencias": [{"nombre": "TEST evidencia editada", "url": "https://example.com/evidencia-editada", "descripcion": "editada"}],
        }
        response = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/seguimientos/{workflow_state['tracking_id']}",
            json=tracking_update,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        tracking = next(item for item in response.json()["seguimientos"] if item["id"] == workflow_state["tracking_id"])
        assert tracking["observaciones"] == "TEST seguimiento editado"

        payment_update = {
            "tipoPago": "PAGO_GENERAL",
            "faseId": None,
            "fechaPago": datetime.utcnow().strftime("%Y-%m-%d"),
            "monto": 1750,
            "metodoPago": "PSE",
            "referencia": "TEST-REF-PAGO-UPD",
            "concepto": "TEST pago general cliente editado",
            "observaciones": "Pago API editado",
        }
        response = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/pagos/{workflow_state['payment_id']}",
            json=payment_update,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        payment = next(item for item in response.json()["pagos"] if item["idPago"] == workflow_state["payment_id"])
        assert float(payment["monto"]) == 1750
        assert payment["metodoPago"] == "PSE"

        assignment_update = {
            "contratistaId": seeded_data["contratista_id"],
            "rol": "TEST Supervisor Obra Editado",
            "fechaInicio": datetime.utcnow().strftime("%Y-%m-%d"),
            "fechaFin": None,
            "valorAcordado": 1250,
            "estado": "ACTIVA",
        }
        response = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/contratistas/{workflow_state['assignment_id']}",
            json=assignment_update,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        assignment = next(item for item in response.json()["contratistasAsignados"] if item["idAsignacion"] == workflow_state["assignment_id"])
        assert assignment["rol"] == "TEST Supervisor Obra Editado"

        temp_assignment_payload = {
            "contratistaId": seeded_data["contratista_id"],
            "rol": "TEST Asignación Eliminable",
            "fechaInicio": datetime.utcnow().strftime("%Y-%m-%d"),
            "fechaFin": None,
            "valorAcordado": 800,
            "estado": "ACTIVA",
        }
        response = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/contratistas",
            json=temp_assignment_payload,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        temp_assignment = next(item for item in response.json()["contratistasAsignados"] if item["rol"] == "TEST Asignación Eliminable")
        workflow_state["temp_assignment_id"] = temp_assignment["idAsignacion"]

        purchase_update = {
            "proveedorId": seeded_data["proveedor_id"],
            "fechaCompra": datetime.utcnow().strftime("%Y-%m-%d"),
            "numeroFactura": "TEST-FAC-UPD",
            "impuesto": 20,
            "observaciones": "TEST compra API editada",
            "detalleCompra": [{"materialId": seeded_data["material_id"], "cantidad": 3, "precioUnitario": 150}],
        }
        response = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/compras/{workflow_state['purchase_id']}",
            json=purchase_update,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        purchase = next(item for item in response.json()["compras"] if item["idCompra"] == workflow_state["purchase_id"])
        assert purchase["numeroFactura"] == "TEST-FAC-UPD"
        assert float(purchase["total"]) == 470

        document_update = {
            "nombre": "TEST Documento URL Editado",
            "url": "https://example.com/planos-test-editado",
            "tipo": "PLANO",
            "seguimientoId": None,
            "observaciones": "Documento editado",
        }
        response = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/documentos/{workflow_state['document_id']}",
            json=document_update,
            timeout=30,
        )
        assert response.status_code == 200, response.text
        document = next(item for item in response.json()["documentos"] if item["id"] == workflow_state["document_id"])
        assert document["tipo"] == "PLANO"
        assert document["nombre"] == "TEST Documento URL Editado"

    def test_17_filters_main_endpoints(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        del seeded_data
        projects = api_client.get(f"{api_base_url}/api/proyectos?q=Casa&estado=EN_EJECUCION&montoMin=1000", timeout=30)
        assert projects.status_code == 200, projects.text
        assert isinstance(projects.json(), list)
        assert all(item["estadoProyecto"] == "EN_EJECUCION" for item in projects.json())

        payments = api_client.get(f"{api_base_url}/api/pagos?q=editado&montoMin=1700&montoMax=1800", timeout=30)
        assert payments.status_code == 200, payments.text
        assert any(item["payment"]["idPago"] == workflow_state["payment_id"] for item in payments.json())

        purchases = api_client.get(f"{api_base_url}/api/compras?q=TEST-FAC-UPD&montoMin=400&montoMax=500", timeout=30)
        assert purchases.status_code == 200, purchases.text
        assert any(item["purchase"]["idCompra"] == workflow_state["purchase_id"] for item in purchases.json())

        documents = api_client.get(f"{api_base_url}/api/documentos?q=Editado", timeout=30)
        assert documents.status_code == 200, documents.text
        assert any(item["document"]["id"] == workflow_state["document_id"] for item in documents.json())

    def test_18_logical_delete_embedded_records_and_summary_recalc(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        payment_create = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/pagos",
            json={
                "tipoPago": "PAGO_GENERAL",
                "faseId": None,
                "fechaPago": datetime.utcnow().strftime("%Y-%m-%d"),
                "monto": 3210,
                "metodoPago": "TRANSFERENCIA",
                "referencia": "TEST-DELETE-PAY",
                "concepto": "TEST pago para eliminar",
                "observaciones": "temporal",
            },
            timeout=30,
        )
        assert payment_create.status_code == 200, payment_create.text
        workflow_state["delete_payment_id"] = payment_create.json()["pagos"][0]["idPago"]
        total_pagado_before = payment_create.json()["resumenFinanciero"]["totalPagadoCliente"]

        purchase_create = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/compras",
            json={
                "proveedorId": seeded_data["proveedor_id"],
                "fechaCompra": datetime.utcnow().strftime("%Y-%m-%d"),
                "numeroFactura": f"TEST-DELETE-PUR-{datetime.utcnow().strftime('%H%M%S')}",
                "impuesto": 10,
                "observaciones": "compra temporal eliminar",
                "detalleCompra": [{"materialId": seeded_data["material_id"], "cantidad": 2, "precioUnitario": 205}],
            },
            timeout=30,
        )
        assert purchase_create.status_code == 200, purchase_create.text
        workflow_state["delete_purchase_id"] = purchase_create.json()["compras"][0]["idCompra"]
        total_compras_before = purchase_create.json()["resumenFinanciero"]["totalCompras"]

        response = api_client.delete(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/fases/{workflow_state['temp_phase_id']}",
            json={"motivo": "fase temporal de prueba"},
            timeout=30,
        )
        assert response.status_code == 200, response.text
        assert all(item["id"] != workflow_state["temp_phase_id"] for item in response.json()["fases"])

        response = api_client.delete(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/contratistas/{workflow_state['temp_assignment_id']}",
            json={"motivo": "asignación temporal de prueba"},
            timeout=30,
        )
        assert response.status_code == 200, response.text
        assert all(item["idAsignacion"] != workflow_state["temp_assignment_id"] for item in response.json()["contratistasAsignados"])

        response = api_client.delete(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/seguimientos/{workflow_state['tracking_id']}",
            json={"motivo": "seguimiento de prueba"},
            timeout=30,
        )
        assert response.status_code == 200, response.text
        assert all(item["id"] != workflow_state["tracking_id"] for item in response.json()["seguimientos"])

        response = api_client.delete(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/pagos/{workflow_state['delete_payment_id']}",
            json={"motivo": "pago de prueba"},
            timeout=30,
        )
        assert response.status_code == 200, response.text
        assert all(item["idPago"] != workflow_state["delete_payment_id"] for item in response.json()["pagos"])
        assert response.json()["resumenFinanciero"]["totalPagadoCliente"] < total_pagado_before

        response = api_client.delete(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/compras/{workflow_state['delete_purchase_id']}",
            json={"motivo": "compra de prueba"},
            timeout=30,
        )
        assert response.status_code == 200, response.text
        assert all(item["idCompra"] != workflow_state["delete_purchase_id"] for item in response.json()["compras"])
        assert response.json()["resumenFinanciero"]["totalCompras"] < total_compras_before

        response = api_client.delete(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/documentos/{workflow_state['document_id']}",
            json={"motivo": "documento de prueba"},
            timeout=30,
        )
        assert response.status_code == 200, response.text
        assert all(item["id"] != workflow_state["document_id"] for item in response.json()["documentos"])

    def test_19_deleted_items_are_excluded_from_feeds(
        self,
        api_client: requests.Session,
        api_base_url: str,
        workflow_state: dict,
    ):
        payments = api_client.get(f"{api_base_url}/api/pagos", timeout=30)
        assert payments.status_code == 200, payments.text
        assert all(item.get("payment", {}).get("idPago") != workflow_state["delete_payment_id"] for item in payments.json())

        purchases = api_client.get(f"{api_base_url}/api/compras", timeout=30)
        assert purchases.status_code == 200, purchases.text
        assert all(item.get("purchase", {}).get("idCompra") != workflow_state["delete_purchase_id"] for item in purchases.json())

        documents = api_client.get(f"{api_base_url}/api/documentos", timeout=30)
        assert documents.status_code == 200, documents.text
        assert all(item.get("document", {}).get("id") != workflow_state["document_id"] for item in documents.json())

    def test_20_critical_validations(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
    ):
        invalid_phase_payment = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/pagos",
            json={
                "tipoPago": "PAGO_POR_FASE",
                "faseId": None,
                "fechaPago": datetime.utcnow().strftime("%Y-%m-%d"),
                "monto": 10,
                "metodoPago": "PSE",
                "referencia": "INV-PHASE",
                "concepto": "Pago inválido",
                "observaciones": "Debe fallar",
            },
            timeout=30,
        )
        assert invalid_phase_payment.status_code == 422

        invalid_tracking = api_client.post(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/seguimientos",
            json={
                "faseId": "fase-no-existe",
                "fecha": datetime.utcnow().strftime("%Y-%m-%d"),
                "observaciones": "Seguimiento inválido",
                "porcentajeAvance": 20,
                "evidencias": [],
            },
            timeout=30,
        )
        assert invalid_tracking.status_code == 404

        project_response = api_client.get(f"{api_base_url}/api/proyectos/{seeded_data['project_id']}", timeout=30)
        project = project_response.json()
        invalid_project_update = api_client.put(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}",
            json={
                "codigoProyecto": project["codigoProyecto"],
                "clienteId": project["clienteId"],
                "nombreProyecto": project["nombreProyecto"],
                "tipoProyecto": project["tipoProyecto"],
                "descripcion": project["descripcion"],
                "ubicacion": project["ubicacion"],
                "area": project["area"],
                "presupuestoEstimado": project["presupuestoEstimado"],
                "valorContrato": project["valorContrato"],
                "estadoProyecto": project["estadoProyecto"],
                "fechaInicio": "2026-12-30",
                "fechaFinEstimada": "2026-01-01",
                "porcentajeAvanceGeneral": project["porcentajeAvanceGeneral"],
                "observacionesGenerales": project["observacionesGenerales"],
                "metodoCalculoAvance": project.get("metodoCalculoAvance", "SEGUIMIENTOS"),
                "fases": [
                    {
                        "nombre": fase["nombre"],
                        "descripcion": fase.get("descripcion", ""),
                        "porcentajePlaneado": fase.get("porcentajePlaneado", 0),
                        "porcentajeAvance": fase.get("porcentajeAvance", 0),
                        "fechaInicio": fase.get("fechaInicio"),
                        "fechaFinEstimada": fase.get("fechaFinEstimada"),
                        "estado": fase.get("estado", "PENDIENTE"),
                    }
                    for fase in project["fases"]
                ],
            },
            timeout=30,
        )
        assert invalid_project_update.status_code == 422

    def test_21_assignment_delete_is_blocked_when_has_history(
        self,
        api_client: requests.Session,
        api_base_url: str,
        seeded_data: dict,
        workflow_state: dict,
    ):
        response = api_client.delete(
            f"{api_base_url}/api/proyectos/{seeded_data['project_id']}/contratistas/{workflow_state['assignment_id']}",
            json={"motivo": "debe fallar por historial"},
            timeout=30,
        )
        assert response.status_code == 409, response.text
