from src.core.settings import Settings
from src.core.lifespan import lifespan
from src.routes.category import routes as category_router
from src.routes.products import routes as product_router
from fastapi import FastAPI
import uvicorn

app = FastAPI(
    title="Ingestion Service",
    description="Reddit comment ingestion for product sentiment analysis",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(category_router)
app.include_router(product_router)

settings = Settings()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.FASTAPI_PORT)
