
"""Domain ports define the interfaces used by the application.

This module must not depend on HTTP, database drivers,
or other project layers.
"""

from typing import Protocol


class DataPort(Protocol):
    """Interface for reading catalogue data and checking database health."""

    def health(self) -> bool:
        """Return whether the database connection is available."""
        ...

    def catalogue(self) -> list[dict]:
        """Return all museum exhibits."""
        ...

    def catalogue_item(self, code: str) -> dict | None:
        """Return one exhibit by its code, or None if it does not exist."""
        ...


class CollectionPort(Protocol):
    """Interface for managing a session-owned museum visit plan.

    Every operation must verify BOTH the collection code
    and the session code.
    """

    def create_or_get(self, session_code: str) -> dict:
        """Create a visit plan or return the existing plan for this session."""
        ...

    def read(self, collection_code: str, session_code: str) -> dict:
        """Read a visit plan belonging to the supplied session."""
        ...

    def add(
        self,
        collection_code: str,
        session_code: str,
        entry: dict
    ) -> None:
        """Add an exhibit and its allocated minutes to a visit plan."""
        ...

    def edit(
        self,
        collection_code: str,
        session_code: str,
        item_code: str,
        entry: dict
    ) -> None:
        """Update an exhibit's allocated minutes in a visit plan."""
        ...

    def remove(
        self,
        collection_code: str,
        session_code: str,
        item_code: str
    ) -> None:
        """Remove an exhibit from a visit plan without deleting its catalogue record."""
        ...
