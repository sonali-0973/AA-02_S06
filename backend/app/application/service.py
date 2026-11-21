
"""Application service for S06: Museum Group Visit Planner."""

from app.domain.ports import DataPort, CollectionPort
from app.domain.scenario import validate_entry, calculate_result
from app.infrastructure.postgres import PostgresData, PostgresCollections


class DataAdapter(DataPort):
    """Adapts the PostgreSQL driver to the catalogue interface."""

    def __init__(self, driver: PostgresData):
        self.driver = driver

    def health(self):
        return self.driver.health()

    def catalogue(self):
        return self.driver.catalogue()

    def catalogue_item(self, code):
        return self.driver.catalogue_item(code)


class StarterService:
    """Coordinates museum catalogue and visit-plan operations."""

    def __init__(
        self,
        data: DataPort,
        collections: CollectionPort | None = None
    ):
        self.data = data
        self.collections = collections

    def _collection_port(self) -> CollectionPort:
        """Ensure the collection adapter has been configured."""
        if self.collections is None:
            raise RuntimeError(
                "Visit-plan storage has not been connected yet."
            )
        return self.collections

    # -----------------------------------------------------
    # Catalogue operations
    # -----------------------------------------------------

    def health(self):
        return self.data.health()

    def catalogue(self):
        return self.data.catalogue()

    def catalogue_item(self, code):
        return self.data.catalogue_item(code)

    # -----------------------------------------------------
    # Visit-plan operations
    # -----------------------------------------------------

    def create_or_get_plan(self, session_code: str) -> dict:
        """Create a plan or return the existing plan for a session."""
        collections = self._collection_port()

        plan = collections.create_or_get(session_code)

        return self.read_plan(
            plan["planCode"],
            session_code
        )

    def read_plan(
        self,
        plan_code: str,
        session_code: str
    ) -> dict:
        """Read the saved plan and calculate its total visit time."""
        collections = self._collection_port()

        plan = collections.read(plan_code, session_code)

        total = calculate_result(
            plan["items"],
            []
        )

        return {
            **plan,
            "totalVisitMinutes": total
        }

    def add_item(
        self,
        plan_code: str,
        session_code: str,
        entry: dict
    ) -> dict:
        """Validate and add an exhibit to the visit plan."""

        # Validate before attempting any database mutation.
        validate_entry(entry)

        exhibit_code = entry.get("exhibitCode")

        if not isinstance(exhibit_code, str) or not exhibit_code:
            raise ValueError("exhibitCode is required.")

        # Confirm the exhibit exists in the seeded catalogue.
        exhibit = self.data.catalogue_item(exhibit_code)

        if exhibit is None:
            raise LookupError("Museum exhibit not found.")

        collections = self._collection_port()

        collections.add(
            plan_code,
            session_code,
            {
                "exhibitCode": exhibit_code,
                "allocatedMinutes": entry["allocatedMinutes"]
            }
        )

        # Return authoritative saved state.
        return self.read_plan(plan_code, session_code)

    def edit_item(
        self,
        plan_code: str,
        session_code: str,
        exhibit_code: str,
        entry: dict
    ) -> dict:
        """Validate and update an existing exhibit allocation."""

        # Invalid values must never reach the database.
        validate_entry(entry)

        collections = self._collection_port()

        collections.edit(
            plan_code,
            session_code,
            exhibit_code,
            {
                "allocatedMinutes": entry["allocatedMinutes"]
            }
        )

        return self.read_plan(plan_code, session_code)

    def remove_item(
        self,
        plan_code: str,
        session_code: str,
        exhibit_code: str
    ) -> dict:
        """Remove a saved stop without deleting its catalogue exhibit."""
        collections = self._collection_port()

        collections.remove(
            plan_code,
            session_code,
            exhibit_code
        )

        return self.read_plan(plan_code, session_code)


def build_service(database_url: str):
    data = DataAdapter(PostgresData(database_url))
    collections = PostgresCollections(database_url)

    return StarterService(
        data=data,
        collections=collections
    )
