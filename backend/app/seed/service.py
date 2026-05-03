from app.core.database import get_database
from app.core.security import hash_password
from app.modules.proyectos.application.service import proyecto_service
from app.seed.data import build_seed_bundle
from app.shared.common import utc_now_iso


async def seed_initial_data():
    database = get_database()
    users_count = await database.usuarios.count_documents({})
    if users_count > 0:
        return

    bundle = build_seed_bundle(hash_password("ArquiControl2026!"), utc_now_iso())

    for project in bundle["proyectos"]:
        proyecto_service._recalculate_project(project)
        proyecto_service.event_publisher.notify("SEED_IMPORTADO", project, "sistema")

    await database.usuarios.insert_many(bundle["usuarios"])
    await database.clientes.insert_many(bundle["clientes"])
    await database.materiales.insert_many(bundle["materiales"])
    await database.proveedores.insert_many(bundle["proveedores"])
    await database.contratistas.insert_many(bundle["contratistas"])
    await database.proyectos.insert_many(bundle["proyectos"])