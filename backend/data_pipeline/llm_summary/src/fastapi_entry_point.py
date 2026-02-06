from fastapi import FastAPI
from src.core.lifespan import lifespan
from src.core.settings_config import Settings
from src.api.routes import router as base_router
import uvicorn

settings = Settings()

app = FastAPI(
    title="LLM summary service",
    description="Fastapi wrapper around LLM summary service so Airflow can call the /run endpoint to invoke the worker.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(base_router)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=settings.FASTAPI_PORT)
