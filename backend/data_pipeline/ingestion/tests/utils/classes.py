from typing import NamedTuple
from fastapi import FastAPI
from fastapi.testclient import TestClient


class FastAPITestClient(NamedTuple):
    client: TestClient
    app: FastAPI
