"""
Script de migración Multi-Tenant para ArquiControl.
===================================================

Este script modifica los archivos del proyecto para que cada usuario
vea solo sus propios datos. Ejecutar desde la raíz del proyecto:

    cd D:\arquicontrol\arquicontrol
    python migrate_multitenant.py

Cambios que realiza:
1. Repositorios de catálogos: agrega filtro userId en list_all y queries de unicidad.
2. Servicios de catálogos: propaga user_id a los repositorios y lo inyecta al crear.
3. Routers de catálogos: pasa current_user.id a los servicios.
4. Repositorio de proyectos: filtra por userId.
5. Servicio de proyectos: propaga user_id.
6. Router de proyectos: pasa current_user.id.
7. Seed: asigna userId al usuario admin en todos los datos iniciales.
"""

import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(BASE, "backend", "app")


def read_file(path):
    full = os.path.join(BASE, path)
    with open(full, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path, content):
    full = os.path.join(BASE, path)
    with open(full, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  ✓ {path}")


def migrate_catalog_repository(module, sort_field, unique_field, unique_method):
    """Genera repositorio multi-tenant para un catálogo."""
    # Determinar imports según módulo
    iface_map = {
        "clientes": ("IClienteRepository", "ClienteRepository"),
        "contratistas": ("IContratistaRepository", "ContratistaRepository"),
        "proveedores": ("IProveedorRepository", "ProveedorRepository"),
        "materiales": ("IMaterialRepository", "MaterialRepository"),
    }
    iface, cls = iface_map[module]
    id_param = {
        "clientes": "client_id",
        "contratistas": "contractor_id",
        "proveedores": "proveedor_id",
        "materiales": "material_id",
    }[module]

    unique_code = ""
    if unique_method == "get_by_document":
        unique_code = f'''
    async def get_by_document(self, document_number: str, user_id: str) -> dict | None:
        return await self.collection.find_one(
            {{"numeroDocumento": document_number, "userId": user_id}}, {{"_id": 0}},
        )
'''
    elif unique_method == "get_by_nit":
        unique_code = f'''
    async def get_by_nit(self, nit: str, user_id: str) -> dict | None:
        return await self.collection.find_one(
            {{"nit": nit, "userId": user_id}}, {{"_id": 0}},
        )
'''
    elif unique_method == "get_by_code":
        unique_code = f'''
    async def get_by_code(self, code: str, user_id: str | None = None) -> dict | None:
        query = {{"codigoMaterial": code}}
        if user_id:
            query["userId"] = user_id
        return await self.collection.find_one(query, {{"_id": 0}})
'''

    content = f'''from app.core.database import get_database
from app.modules.{module}.domain.repositories import {iface}


class {cls}({iface}):
    def __init__(self):
        self.collection = get_database().{module}

    async def list_all(self, user_id: str | None = None) -> list[dict]:
        query = {{"userId": user_id}} if user_id else {{}}
        cursor = self.collection.find(query, {{"_id": 0}}).sort("{sort_field}", 1)
        return await cursor.to_list(500)

    async def get_by_id(self, {id_param}: str) -> dict | None:
        return await self.collection.find_one({{"id": {id_param}}}, {{"_id": 0}})
{unique_code}
    async def create(self, data: dict) -> dict:
        await self.collection.insert_one(dict(data))
        return data

    async def update(self, {id_param}: str, data: dict) -> dict | None:
        await self.collection.update_one({{"id": {id_param}}}, {{"$set": data}})
        return await self.get_by_id({id_param})
'''
    write_file(f"backend/app/modules/{module}/infrastructure/repository.py", content)


def migrate_catalog_service(module, unique_field, unique_method, entity_name, response_cls):
    """Genera servicio multi-tenant para un catálogo."""
    imports_map = {
        "clientes": "from app.modules.clientes.domain.models import ClienteCreate, ClienteResponse, ClienteUpdate\nfrom app.modules.clientes.infrastructure.repository import ClienteRepository",
        "contratistas": "from app.modules.contratistas.domain.models import ContratistaCreate, ContratistaResponse, ContratistaUpdate\nfrom app.modules.contratistas.infrastructure.repository import ContratistaRepository",
        "proveedores": "from app.modules.proveedores.domain.models import ProveedorCreate, ProveedorResponse, ProveedorUpdate\nfrom app.modules.proveedores.infrastructure.repository import ProveedorRepository",
        "materiales": "from app.modules.materiales.domain.models import MaterialCreate, MaterialResponse, MaterialUpdate\nfrom app.modules.materiales.infrastructure.repository import MaterialRepository",
    }
    cls_map = {
        "clientes": ("ClienteService", "ClienteRepository", "ClienteCreate", "ClienteUpdate", "ClienteResponse"),
        "contratistas": ("ContratistaService", "ContratistaRepository", "ContratistaCreate", "ContratistaUpdate", "ContratistaResponse"),
        "proveedores": ("ProveedorService", "ProveedorRepository", "ProveedorCreate", "ProveedorUpdate", "ProveedorResponse"),
        "materiales": ("MaterialService", "MaterialRepository", "MaterialCreate", "MaterialUpdate", "MaterialResponse"),
    }
    svc_cls, repo_cls, create_cls, update_cls, resp_cls = cls_map[module]
    id_param = {"clientes": "client_id", "contratistas": "contractor_id", "proveedores": "proveedor_id", "materiales": "material_id"}[module]

    # Unique check call
    if unique_method == "get_by_document":
        unique_check_create = f'await self.repository.get_by_document(payload.{unique_field}, user_id)'
        unique_check_update = f'await self.repository.get_by_document(payload.{unique_field}, user_id)'
        dup_msg = f'"{entity_name} ya registrado con ese documento"'
    elif unique_method == "get_by_nit":
        unique_check_create = f'await self.repository.get_by_nit(payload.{unique_field}, user_id)'
        unique_check_update = f'await self.repository.get_by_nit(payload.{unique_field}, user_id)'
        dup_msg = '"NIT ya registrado"'
    elif unique_method == "get_by_code":
        unique_check_create = f'await self.repository.get_by_code(payload.{unique_field}, user_id)'
        unique_check_update = f'await self.repository.get_by_code(payload.{unique_field}, user_id)'
        dup_msg = '"Código de material ya registrado"'
    else:
        unique_check_create = unique_check_update = 'None'
        dup_msg = '"Duplicado"'

    content = f'''from fastapi import HTTPException, status

{imports_map[module]}
from app.shared.common import create_audit_fields, touch_updated_at


class {svc_cls}:
    def __init__(self, repository: {repo_cls}):
        self.repository = repository

    async def list_all(self, user_id: str) -> list[{resp_cls}]:
        return [{resp_cls}(**item) for item in await self.repository.list_all(user_id)]

    async def create(self, payload: {create_cls}, user_id: str) -> {resp_cls}:
        existing = {unique_check_create}
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={dup_msg})
        data = {{**payload.model_dump(), **create_audit_fields(), "userId": user_id}}
        created = await self.repository.create(data)
        return {resp_cls}(**created)

    async def update(self, {id_param}: str, payload: {update_cls}, user_id: str) -> {resp_cls}:
        current = await self.repository.get_by_id({id_param})
        if not current or current.get("userId") != user_id:
            raise HTTPException(status_code=404, detail="{entity_name} no encontrado")
        duplicated = {unique_check_update}
        if duplicated and duplicated["id"] != {id_param}:
            raise HTTPException(status_code=409, detail={dup_msg})
        updated = touch_updated_at({{**current, **payload.model_dump()}})
        saved = await self.repository.update({id_param}, updated)
        return {resp_cls}(**saved)


{module}_service = {svc_cls}({repo_cls}())
'''
    # Fix variable name for singleton
    singleton_name = {"clientes": "cliente", "contratistas": "contratista", "proveedores": "proveedor", "materiales": "material"}[module]
    content = content.replace(f"{module}_service", f"{singleton_name}_service")
    write_file(f"backend/app/modules/{module}/application/service.py", content)


def migrate_catalog_router(module, entity_name):
    """Genera router multi-tenant para un catálogo."""
    maps = {
        "clientes": {
            "svc_import": "from app.modules.clientes.application.service import cliente_service",
            "model_import": "from app.modules.clientes.domain.models import ClienteCreate, ClienteResponse, ClienteUpdate",
            "svc": "cliente_service", "prefix": "/clientes", "tag": "clientes",
            "id_param": "client_id",
            "create_cls": "ClienteCreate", "update_cls": "ClienteUpdate", "resp_cls": "ClienteResponse",
        },
        "contratistas": {
            "svc_import": "from app.modules.contratistas.application.service import contratista_service",
            "model_import": "from app.modules.contratistas.domain.models import ContratistaCreate, ContratistaResponse, ContratistaUpdate",
            "svc": "contratista_service", "prefix": "/contratistas", "tag": "contratistas",
            "id_param": "contratista_id",
            "create_cls": "ContratistaCreate", "update_cls": "ContratistaUpdate", "resp_cls": "ContratistaResponse",
        },
        "proveedores": {
            "svc_import": "from app.modules.proveedores.application.service import proveedor_service",
            "model_import": "from app.modules.proveedores.domain.models import ProveedorCreate, ProveedorResponse, ProveedorUpdate",
            "svc": "proveedor_service", "prefix": "/proveedores", "tag": "proveedores",
            "id_param": "proveedor_id",
            "create_cls": "ProveedorCreate", "update_cls": "ProveedorUpdate", "resp_cls": "ProveedorResponse",
        },
        "materiales": {
            "svc_import": "from app.modules.materiales.application.service import material_service",
            "model_import": "from app.modules.materiales.domain.models import MaterialCreate, MaterialResponse, MaterialUpdate",
            "svc": "material_service", "prefix": "/materiales", "tag": "materiales",
            "id_param": "material_id",
            "create_cls": "MaterialCreate", "update_cls": "MaterialUpdate", "resp_cls": "MaterialResponse",
        },
    }
    m = maps[module]
    content = f'''from fastapi import APIRouter, Depends

from app.modules.auth.application.service import get_current_user
from app.modules.auth.domain.models import UserResponse
{m["svc_import"]}
{m["model_import"]}


router = APIRouter(prefix="{m["prefix"]}", tags=["{m["tag"]}"])


@router.get("", response_model=list[{m["resp_cls"]}])
async def list_{module}(current_user: UserResponse = Depends(get_current_user)):
    return await {m["svc"]}.list_all(current_user.id)


@router.post("", response_model={m["resp_cls"]})
async def create_{entity_name}(
    payload: {m["create_cls"]},
    current_user: UserResponse = Depends(get_current_user),
):
    return await {m["svc"]}.create(payload, current_user.id)


@router.put("/{{{m["id_param"]}}}", response_model={m["resp_cls"]})
async def update_{entity_name}(
    {m["id_param"]}: str,
    payload: {m["update_cls"]},
    current_user: UserResponse = Depends(get_current_user),
):
    return await {m["svc"]}.update({m["id_param"]}, payload, current_user.id)
'''
    write_file(f"backend/app/modules/{module}/presentation/router.py", content)


def migrate_proyectos_repository():
    """Agrega filtro userId al repositorio de proyectos."""
    path = "backend/app/modules/proyectos/infrastructure/repository.py"
    content = read_file(path)

    # Reemplazar list_all para filtrar por userId
    content = content.replace(
        'cursor = self.collection.find({}).sort("updatedAt", -1)',
        '''async def list_all(self, user_id: str | None = None) -> list[dict]:
        query = {"userId": user_id} if user_id else {}
        cursor = self.collection.find(query, {"_id": 0}).sort("updatedAt", -1)'''
    )
    # Esto puede ser complejo, mejor reescribo el método directamente
    orig = read_file(path)

    # Simple approach: replace the list_all method
    new_content = orig.replace(
        '''    async def list_all(self) -> list[dict]:
        cursor = self.collection.find({}).sort("updatedAt", -1)
        return await cursor.to_list(length=500)''',
        '''    async def list_all(self, user_id: str | None = None) -> list[dict]:
        query = {"userId": user_id} if user_id else {}
        cursor = self.collection.find(query, {"_id": 0}).sort("updatedAt", -1)
        return await cursor.to_list(length=500)'''
    )
    write_file(path, new_content)


def migrate_proyectos_service():
    """Agrega userId al servicio de proyectos en create y list_all."""
    path = "backend/app/modules/proyectos/application/service.py"
    content = read_file(path)

    # 1. Modificar list_all para recibir y pasar user_id
    content = content.replace(
        'async def list_all(self, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None) -> list[ProyectoResponse]:',
        'async def list_all(self, user_id: str, q=None, estado=None, cliente_id=None, fecha_desde=None, fecha_hasta=None, monto_min=None, monto_max=None) -> list[ProyectoResponse]:'
    )
    content = content.replace(
        'projects = await self.repository.list_all()',
        'projects = await self.repository.list_all(user_id)'
    )

    # 2. Modificar create para inyectar userId
    content = content.replace(
        '"compras": [], "documentos": [], "resumenFinanciero": {},',
        '"compras": [], "documentos": [], "resumenFinanciero": {}, "userId": actor_user_id,'
    )

    # Cambiar firma de create para recibir user_id
    content = content.replace(
        'async def create(self, payload: ProyectoCreate, actor: str) -> ProyectoResponse:',
        'async def create(self, payload: ProyectoCreate, actor: str, actor_user_id: str = "") -> ProyectoResponse:'
    )

    # 3. Modificar get_by_id para validar ownership
    content = content.replace(
        '''    async def get_by_id(self, project_id: str, include_inactive: bool = False) -> ProyectoResponse:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")''',
        '''    async def get_by_id(self, project_id: str, include_inactive: bool = False, user_id: str | None = None) -> ProyectoResponse:
        project = await self.repository.get_by_id(project_id)
        if not project or (user_id and project.get("userId") and project["userId"] != user_id):
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")'''
    )

    write_file(path, content)


def migrate_proyectos_router():
    """Agrega current_user.id a las llamadas del router de proyectos."""
    path = "backend/app/modules/proyectos/presentation/router.py"
    content = read_file(path)

    # Modificar list_projects para pasar user_id
    content = content.replace(
        'return await proyecto_service.list_all(q=q',
        'return await proyecto_service.list_all(user_id=current_user.id, q=q'
    )

    # Para list_projects, cambiar _ a current_user
    # Find the list_projects endpoint and change _ to current_user
    content = content.replace(
        '''async def list_projects(
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    clienteId: str | None = Query(default=None),
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    montoMin: float | None = Query(default=None),
    montoMax: float | None = Query(default=None),
    _: UserResponse = Depends(get_current_user),''',
        '''async def list_projects(
    q: str | None = Query(default=None),
    estado: str | None = Query(default=None),
    clienteId: str | None = Query(default=None),
    fechaDesde: str | None = Query(default=None),
    fechaHasta: str | None = Query(default=None),
    montoMin: float | None = Query(default=None),
    montoMax: float | None = Query(default=None),
    current_user: UserResponse = Depends(get_current_user),'''
    )

    # Modify create_project to pass user_id
    content = content.replace(
        'return await proyecto_service.create(payload, current_user.email)',
        'return await proyecto_service.create(payload, current_user.email, actor_user_id=current_user.id)'
    )

    # Modify get_project to pass user_id
    content = content.replace(
        '''async def get_project(project_id: str, _: UserResponse = Depends(get_current_user)):
    return await proyecto_service.get_by_id(project_id)''',
        '''async def get_project(project_id: str, current_user: UserResponse = Depends(get_current_user)):
    return await proyecto_service.get_by_id(project_id, user_id=current_user.id)'''
    )

    write_file(path, content)


def migrate_seed():
    """Agrega userId al seed data para el usuario admin."""
    path = "backend/app/seed/service.py"
    content = read_file(path)

    # Agregar userId a cada bundle antes de insertar
    # Buscar la línea donde se insertan los datos y agregar userId
    if "userId" not in content:
        content = content.replace(
            'await database.clientes.insert_many(bundle["clientes"])',
            '''# Asignar userId del admin a todos los datos seed
        admin_user_id = bundle["usuarios"][0]["id"]
        for collection_name in ["clientes", "contratistas", "proveedores", "materiales", "proyectos"]:
            for doc in bundle.get(collection_name, []):
                doc["userId"] = admin_user_id

        await database.clientes.insert_many(bundle["clientes"])'''
        )

    write_file(path, content)


def migrate_feed_service():
    """Agrega filtro userId a los feeds transversales."""
    path = "backend/app/modules/proyectos/application/feed_service.py"
    content = read_file(path)

    # Cambiar los métodos de feed para recibir user_id
    for method in ["get_payments_feed", "get_purchases_feed", "get_documents_feed"]:
        content = content.replace(
            f'async def {method}(\n        self, q=None',
            f'async def {method}(\n        self, user_id: str | None = None, q=None'
        )

    # Cambiar list_all() a list_all(user_id) en los feeds
    content = content.replace(
        'projects = await self.repository.list_all()',
        'projects = await self.repository.list_all(user_id)'
    )

    write_file(path, content)


def main():
    print("=" * 60)
    print("  Migración Multi-Tenant para ArquiControl")
    print("=" * 60)
    print()

    # 1. Catálogos
    print("1. Migrando catálogos...")

    migrate_catalog_repository("clientes", "nombreCompleto", "numeroDocumento", "get_by_document")
    migrate_catalog_service("clientes", "numeroDocumento", "get_by_document", "Cliente", "ClienteResponse")
    migrate_catalog_router("clientes", "cliente")

    migrate_catalog_repository("contratistas", "nombreCompleto", "numeroDocumento", "get_by_document")
    migrate_catalog_service("contratistas", "numeroDocumento", "get_by_document", "Contratista", "ContratistaResponse")
    migrate_catalog_router("contratistas", "contratista")

    migrate_catalog_repository("proveedores", "nombre", "nit", "get_by_nit")
    migrate_catalog_service("proveedores", "nit", "get_by_nit", "Proveedor", "ProveedorResponse")
    migrate_catalog_router("proveedores", "proveedor")

    migrate_catalog_repository("materiales", "nombre", "codigoMaterial", "get_by_code")
    migrate_catalog_service("materiales", "codigoMaterial", "get_by_code", "Material", "MaterialResponse")
    migrate_catalog_router("materiales", "material")

    # 2. Proyectos
    print("\n2. Migrando proyectos...")
    migrate_proyectos_repository()
    migrate_proyectos_service()
    migrate_proyectos_router()

    # 3. Feeds
    print("\n3. Migrando feeds...")
    migrate_feed_service()

    # 4. Seed
    print("\n4. Migrando seed...")
    migrate_seed()

    print()
    print("=" * 60)
    print("  ✓ Migración completada")
    print("=" * 60)
    print()
    print("Próximos pasos:")
    print("  1. Reinicia el backend (uvicorn se recarga con --reload)")
    print("  2. Borra las colecciones en Atlas (Browse Collections → Drop)")
    print("     para que el seed regenere los datos con userId")
    print("  3. Reinicia el backend de nuevo para que ejecute el seed")
    print("  4. Prueba: login con admin → verás los 3 proyectos")
    print("  5. Prueba: registra un nuevo usuario → verá todo vacío")
    print("  6. El nuevo usuario crea sus propios clientes/proyectos")
    print()


if __name__ == "__main__":
    main()