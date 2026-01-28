from src.core.lifespan import lifespan
from src.core.settings_config import Settings
from src.api.routes import router as base_router
from fastapi import FastAPI

app = FastAPI(
    title="Ingestion Service",
    description="Reddit comment ingestion for product sentiment analysis",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(base_router)

settings = Settings()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.FASTAPI_PORT)
