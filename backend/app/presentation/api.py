
"""HTTP API routes for S06: Museum Group Visit Planner."""

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, StrictInt, Field

from app.application.service import StarterService


# Every visit-plan request must include this header.
Session = Annotated[
    str,
    Header(alias="X-Session-Code", min_length=1, max_length=128)
]


class AddExhibitRequest(BaseModel):
    """Request body for adding an exhibit."""
    exhibitCode: str = Field(min_length=1, max_length=64)
    allocatedMinutes: StrictInt = Field(ge=5, le=60)


class EditAllocationRequest(BaseModel):
    """Request body for editing an exhibit allocation."""
    allocatedMinutes: StrictInt = Field(ge=5, le=60)


def routes(service: StarterService):
    router = APIRouter(prefix="/api")

    # -----------------------------------------------------
    # EXHIBIT CATALOGUE
    # -----------------------------------------------------

    @router.get("/health")
    def health():
        if not service.health():
            raise HTTPException(
                status_code=503,
                detail="Database unavailable."
            )

        return {
            "status": "ok",
            "database": "connected"
        }

    @router.get("/exhibits")
    def get_exhibits():
        return {
            "items": service.catalogue()
        }

    @router.get("/exhibits/{exhibitCode}")
    def get_exhibit(exhibitCode: str):
        exhibit = service.catalogue_item(exhibitCode)

        if exhibit is None:
            raise HTTPException(
                status_code=404,
                detail="Museum exhibit not found."
            )

        return exhibit

    # -----------------------------------------------------
    # CREATE OR RETURN VISIT PLAN
    # -----------------------------------------------------

    @router.post("/visit-plans")
    def create_visit_plan(session_code: Session):
        try:
            return service.create_or_get_plan(session_code)

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc)
            )

    # -----------------------------------------------------
    # READ VISIT PLAN
    # -----------------------------------------------------

    @router.get("/visit-plans/{planCode}")
    def get_visit_plan(
        planCode: str,
        session_code: Session
    ):
        try:
            return service.read_plan(
                planCode,
                session_code
            )

        except LookupError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc)
            )

    # -----------------------------------------------------
    # ADD EXHIBIT
    # -----------------------------------------------------

    @router.post("/visit-plans/{planCode}/items")
    def add_exhibit(
        planCode: str,
        entry: AddExhibitRequest,
        session_code: Session
    ):
        try:
            return service.add_item(
                planCode,
                session_code,
                entry.model_dump()
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc)
            )

        except LookupError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc)
            )

    # -----------------------------------------------------
    # EDIT EXHIBIT ALLOCATION
    # -----------------------------------------------------

    @router.put("/visit-plans/{planCode}/items/{exhibitCode}")
    def edit_exhibit(
        planCode: str,
        exhibitCode: str,
        entry: EditAllocationRequest,
        session_code: Session
    ):
        try:
            return service.edit_item(
                planCode,
                session_code,
                exhibitCode,
                entry.model_dump()
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=422,
                detail=str(exc)
            )

        except LookupError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc)
            )

    # -----------------------------------------------------
    # REMOVE EXHIBIT
    # -----------------------------------------------------

    @router.delete("/visit-plans/{planCode}/items/{exhibitCode}")
    def remove_exhibit(
        planCode: str,
        exhibitCode: str,
        session_code: Session
    ):
        try:
            return service.remove_item(
                planCode,
                session_code,
                exhibitCode
            )

        except LookupError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc)
            )

        except RuntimeError as exc:
            raise HTTPException(
                status_code=503,
                detail=str(exc)
            )

    return router
