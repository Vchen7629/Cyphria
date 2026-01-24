from fastapi import FastAPI
from fastapi.testclient import TestClient
from typing import NamedTuple

class FastAPITestClient(NamedTuple):
    client: TestClient
    app: FastAPI