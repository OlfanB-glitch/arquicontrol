"""
Definición centralizada de índices de MongoDB para ArquiControl.

Los índices mejoran el rendimiento de consultas frecuentes y garantizan
unicidad a nivel de base de datos, protegiendo contra race conditions
que la validación en capa de servicio no puede cubrir.

La función `ensure_indexes()` se ejecuta en el evento `startup` de FastAPI.
MongoDB ignora la creación de un índice que ya existe, por lo que es seguro
llamarla en cada arranque del servidor.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING


logger = logging.getLogger(__name__)


async def ensure_indexes(database: AsyncIOMotorDatabase) -> None:
    """Crea todos los índices requeridos por ArquiControl.

    Se invoca una sola vez durante el arranque de la aplicación.
    """

    # --- usuarios ---
    # email: único -> garantiza que no existan dos cuentas con el mismo correo
    # id: único -> acelera get_by_id tras validar JWT
    await database.usuarios.create_index(
        [("email", ASCENDING)], unique=True, name="uq_usuarios_email",
    )
    await database.usuarios.create_index(
        [("id", ASCENDING)], unique=True, name="uq_usuarios_id",
    )

    # --- clientes ---
    # numeroDocumento: único -> regla de negocio (un cliente = un documento)
    # id: único -> búsqueda por ID al referenciar desde proyectos
    # nombreCompleto: ordenamiento ascendente usado en list_all()
    await database.clientes.create_index(
        [("numeroDocumento", ASCENDING)], unique=True, name="uq_clientes_documento",
    )
    await database.clientes.create_index(
        [("id", ASCENDING)], unique=True, name="uq_clientes_id",
    )
    await database.clientes.create_index(
        [("nombreCompleto", ASCENDING)], name="ix_clientes_nombre",
    )

    # --- contratistas ---
    await database.contratistas.create_index(
        [("numeroDocumento", ASCENDING)], unique=True, name="uq_contratistas_documento",
    )
    await database.contratistas.create_index(
        [("id", ASCENDING)], unique=True, name="uq_contratistas_id",
    )
    await database.contratistas.create_index(
        [("nombreCompleto", ASCENDING)], name="ix_contratistas_nombre",
    )

    # --- proveedores ---
    # nit: único -> regla de negocio (un proveedor = un NIT)
    await database.proveedores.create_index(
        [("nit", ASCENDING)], unique=True, name="uq_proveedores_nit",
    )
    await database.proveedores.create_index(
        [("id", ASCENDING)], unique=True, name="uq_proveedores_id",
    )
    await database.proveedores.create_index(
        [("nombre", ASCENDING)], name="ix_proveedores_nombre",
    )

    # --- materiales ---
    # codigoMaterial: único -> regla de negocio (código único por material)
    await database.materiales.create_index(
        [("codigoMaterial", ASCENDING)], unique=True, name="uq_materiales_codigo",
    )
    await database.materiales.create_index(
        [("id", ASCENDING)], unique=True, name="uq_materiales_id",
    )
    await database.materiales.create_index(
        [("nombre", ASCENDING)], name="ix_materiales_nombre",
    )

    # --- proyectos ---
    # codigoProyecto: único -> regla de negocio
    # clienteId: acelera filtros por cliente en el listado
    # estadoProyecto: acelera filtros por estado
    # updatedAt descendente: ordenamiento en list_all()
    await database.proyectos.create_index(
        [("codigoProyecto", ASCENDING)], unique=True, name="uq_proyectos_codigo",
    )
    await database.proyectos.create_index(
        [("id", ASCENDING)], unique=True, name="uq_proyectos_id",
    )
    await database.proyectos.create_index(
        [("clienteId", ASCENDING)], name="ix_proyectos_cliente",
    )
    await database.proyectos.create_index(
        [("estadoProyecto", ASCENDING)], name="ix_proyectos_estado",
    )
    await database.proyectos.create_index(
        [("updatedAt", DESCENDING)], name="ix_proyectos_updatedAt",
    )

    logger.info("Índices de MongoDB verificados correctamente")