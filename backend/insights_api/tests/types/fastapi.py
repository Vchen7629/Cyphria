
from typing import NamedTuple
from fastapi import FastAPI
from httpx import AsyncClient

class FastAPITestClient(NamedTuple):
    client: AsyncClient
    app: FastAPI