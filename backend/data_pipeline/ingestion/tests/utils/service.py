from typing import Any
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def null_lifespan(_app: FastAPI) -> Any:
    """No-op lifespan for testing - state is set by fixtures"""
    yield

