from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from dental_clinic.db.base import Base
from dental_clinic.db.session import engine
import dental_clinic.models  # noqa: F401
from dental_clinic.routers.auth import router as auth_router
from dental_clinic.routers.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Dental Clinic Appointment API",
        lifespan=lifespan,
    )
    app.include_router(auth_router)
    app.include_router(health_router)
    return app


app = create_app()