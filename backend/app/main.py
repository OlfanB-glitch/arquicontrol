import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import MongoConnection, get_database
from app.core.indexes import ensure_indexes
from app.modules.auth.presentation.router import router as auth_router
from app.modules.clientes.presentation.router import router as clientes_router
from app.modules.contratistas.presentation.router import router as contratistas_router
from app.modules.dashboard.presentation.router import router as dashboard_router
from app.modules.materiales.presentation.router import router as materiales_router
from app.modules.proveedores.presentation.router import router as proveedores_router
from app.modules.proyectos.presentation.router import router as proyectos_router
from app.seed.service import seed_initial_data


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title=settings.project_name)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get(f"{settings.api_prefix}/health")
    async def health_check():
        return {"status": "ok", "service": settings.project_name}

    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(dashboard_router, prefix=settings.api_prefix)
    app.include_router(clientes_router, prefix=settings.api_prefix)
    app.include_router(proyectos_router, prefix=settings.api_prefix)
    app.include_router(contratistas_router, prefix=settings.api_prefix)
    app.include_router(proveedores_router, prefix=settings.api_prefix)
    app.include_router(materiales_router, prefix=settings.api_prefix)

    @app.on_event("startup")
    async def on_startup():
        settings.uploads_dir.mkdir(parents=True, exist_ok=True)
        await ensure_indexes(get_database())
        await seed_initial_data()
        logger.info("ArquiControl listo")

    @app.on_event("shutdown")
    async def on_shutdown():
        MongoConnection().close()

    return app