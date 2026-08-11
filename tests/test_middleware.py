from __future__ import annotations

import re

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middleware import CorrelationIdMiddleware


def test_correlation_id_middleware_sets_request_state_and_response_headers() -> None:
    app = FastAPI()

    @app.get("/test")
    async def route(request: Request) -> dict[str, str]:
        return {"correlation_id": request.state.correlation_id}

    app.add_middleware(CorrelationIdMiddleware)

    with TestClient(app) as client:
        response = client.get("/test", headers={"x-request-id": "req-12345678"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-12345678"
    assert response.headers["x-response-time-ms"].isdigit()
    assert response.json()["correlation_id"] == "req-12345678"


def test_correlation_id_middleware_generates_format_when_header_missing() -> None:
    app = FastAPI()

    @app.get("/test")
    async def route(request: Request) -> dict[str, str]:
        return {"correlation_id": request.state.correlation_id}

    app.add_middleware(CorrelationIdMiddleware)

    with TestClient(app) as client:
        response = client.get("/test")

    assert response.status_code == 200
    assert re.fullmatch(r"req-[0-9a-f]{8}", response.headers["x-request-id"])
    assert response.json()["correlation_id"] == response.headers["x-request-id"]
