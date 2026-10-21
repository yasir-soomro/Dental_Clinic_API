from contextlib import asynccontextmanager

from fastapi import FastAPI

from dental_clinic.db.database import Base, engine
from dental_clinic.models.user import User  # Register the model
from dental_clinic.routers.auth import router as auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Dental Clinic Appointment API",
    lifespan=lifespan,
)

app.include_router(auth_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}