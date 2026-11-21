"""HTTP translation only; project dependencies are application-only."""
from typing import Annotated
from fastapi import APIRouter, Header, HTTPException
from app.application.service import StarterService

Session = Annotated[str, Header(alias="X-Session-Code", min_length=1, max_length=128)]

def routes(service: StarterService):
    router = APIRouter(prefix="/api")
    @router.get("/health")
    def health():
        if not service.health(): raise HTTPException(503, "Database unavailable")
        return {"status": "ok", "database": "connected", "scope": "bootstrap only"}
    @router.get("/catalogue")
    def catalogue(): return {"items": service.catalogue(), "scope": "neutral bootstrap data"}
    @router.get("/catalogue/{item_code}")
    def detail(item_code: str):
        item = service.catalogue_item(item_code)
        if item is None: raise HTTPException(404, "Catalogue item not found")
        return item
    # TODO: rename routes/fields and implement scenario request/response models.
    # Stubs cannot access or mutate any collection; they return explicit 501.
    @router.post("/collections")
    def create(session_code: Session): return service.collection_todo()
    @router.get("/collections/{collection_code}")
    def read(collection_code: str, session_code: Session): return service.collection_todo()
    @router.post("/collections/{collection_code}/items")
    def add(collection_code: str, entry: dict, session_code: Session): return service.collection_todo()
    @router.put("/collections/{collection_code}/items/{item_code}")
    def edit(collection_code: str, item_code: str, entry: dict, session_code: Session): return service.collection_todo()
    @router.delete("/collections/{collection_code}/items/{item_code}")
    def remove(collection_code: str, item_code: str, session_code: Session): return service.collection_todo()
    return router
