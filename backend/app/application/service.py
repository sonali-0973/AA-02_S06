"""Application adapters implement domain ports and orchestrate infrastructure."""
from app.domain.ports import DataPort
from app.infrastructure.postgres import PostgresData

class DataAdapter(DataPort):
    def __init__(self, driver: PostgresData): self.driver = driver
    def health(self): return self.driver.health()
    def catalogue(self): return self.driver.catalogue()
    def catalogue_item(self, code): return self.driver.catalogue_item(code)

class StarterService:
    def __init__(self, data: DataPort): self.data = data
    def health(self): return self.data.health()
    def catalogue(self): return self.data.catalogue()
    def catalogue_item(self, code): return self.data.catalogue_item(code)
    def collection_todo(self):
        # TODO: implement CollectionPort, ownership checks, domain validation,
        # transactional persistence, authoritative read and domain calculation.
        raise NotImplementedError("Implement your assigned session-owned workflow")

def build_service(database_url: str):
    return StarterService(DataAdapter(PostgresData(database_url)))
