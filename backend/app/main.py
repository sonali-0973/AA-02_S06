"""Composition root and common error translation."""
import logging
import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.application.service import build_service
from app.presentation.api import routes

def create_app(service=None):
    app = FastAPI(title="AA-02 scenario starter", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.include_router(routes(service or build_service(os.environ["DATABASE_URL"])))
    @app.exception_handler(NotImplementedError)
    async def todo(request: Request, exc):
        return JSONResponse(status_code=501, content={"error_code": "SCENARIO_TODO", "message": str(exc)})
    @app.exception_handler(RequestValidationError)
    async def invalid(request: Request, exc):
        return JSONResponse(status_code=400, content={"error_code": "INVALID_REQUEST", "message": "Check request fields and X-Session-Code."})
    @app.exception_handler(Exception)
    async def unavailable(request: Request, exc):
        logging.exception("Request failed: %s", request.url.path)
        return JSONResponse(status_code=503, content={"error_code": "SERVICE_UNAVAILABLE", "message": "Check API/database logs."})
    return app

app = create_app()
