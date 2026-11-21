"""Replaceable database driver; no dependencies on other project layers."""
import psycopg
from psycopg.rows import dict_row

class PostgresData:
    def __init__(self, url: str):
        self.url = url

    def _read(self, sql: str, values: tuple = ()) -> list[dict]:
        with psycopg.connect(self.url, row_factory=dict_row, connect_timeout=3) as connection:
            return connection.execute(sql, values).fetchall()

    def health(self) -> bool:
        return self._read("SELECT 1 AS connected") == [{"connected": 1}]

    def catalogue(self) -> list[dict]:
        return self._read("SELECT code, name, details FROM catalogue_items ORDER BY code")

    def catalogue_item(self, code: str) -> dict | None:
        rows = self._read("SELECT code, name, details FROM catalogue_items WHERE code = %s", (code,))
        return rows[0] if rows else None

    # TODO: parameterised, transactional collection persistence operations.
    # Enforce session ownership in every query, validate before mutations,
    # and DELETE only an entry, never its seeded catalogue record.
