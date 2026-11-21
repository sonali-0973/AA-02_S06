
"""PostgreSQL database operations for S06 Museum Group Visit Planner."""

import uuid

import psycopg
from psycopg.rows import dict_row


class PostgresData:
    """Reads the museum exhibit catalogue."""

    def __init__(self, url: str):
        self.url = url

    def health(self) -> bool:
        with psycopg.connect(
            self.url,
            row_factory=dict_row,
            connect_timeout=3
        ) as connection:
            row = connection.execute(
                "SELECT 1 AS connected"
            ).fetchone()
            return row["connected"] == 1

    def catalogue(self) -> list[dict]:
        with psycopg.connect(
            self.url,
            row_factory=dict_row,
            connect_timeout=3
        ) as connection:
            rows = connection.execute("""
                SELECT
                    code,
                    name,
                    theme,
                    suggested_minutes AS "suggestedMinutes"
                FROM exhibits
                ORDER BY code
            """).fetchall()

            return [dict(row) for row in rows]

    def catalogue_item(self, code: str) -> dict | None:
        with psycopg.connect(
            self.url,
            row_factory=dict_row,
            connect_timeout=3
        ) as connection:
            row = connection.execute("""
                SELECT
                    code,
                    name,
                    theme,
                    suggested_minutes AS "suggestedMinutes"
                FROM exhibits
                WHERE code = %s
            """, (code,)).fetchone()

            return dict(row) if row else None


class PostgresCollections:
    """Creates and manages session-owned visit plans."""

    def __init__(self, url: str):
        self.url = url

    def create_or_get(self, session_code: str) -> dict:
        new_code = f"PLAN-{uuid.uuid4().hex[:12].upper()}"

        with psycopg.connect(
            self.url,
            row_factory=dict_row,
            connect_timeout=3
        ) as connection:
            row = connection.execute("""
                INSERT INTO visit_plans (code, session_code)
                VALUES (%s, %s)
                ON CONFLICT (session_code)
                DO UPDATE SET session_code = EXCLUDED.session_code
                RETURNING code
            """, (new_code, session_code)).fetchone()

            return {"planCode": row["code"]}

    def read(self, collection_code: str, session_code: str) -> dict:
        with psycopg.connect(
            self.url,
            row_factory=dict_row,
            connect_timeout=3
        ) as connection:

            plan = connection.execute("""
                SELECT code
                FROM visit_plans
                WHERE code = %s AND session_code = %s
            """, (collection_code, session_code)).fetchone()

            if plan is None:
                raise LookupError("Visit plan not found.")

            rows = connection.execute("""
                SELECT
                    e.code AS "exhibitCode",
                    e.name,
                    e.theme,
                    e.suggested_minutes AS "suggestedMinutes",
                    i.allocated_minutes AS "allocatedMinutes"
                FROM visit_plan_items i
                JOIN exhibits e ON e.code = i.exhibit_code
                WHERE i.plan_code = %s
                ORDER BY e.code
            """, (collection_code,)).fetchall()

            return {
                "planCode": plan["code"],
                "items": [dict(row) for row in rows]
            }

    def add(
        self,
        collection_code: str,
        session_code: str,
        entry: dict
    ) -> None:
        with psycopg.connect(self.url, connect_timeout=3) as connection:

            plan = connection.execute("""
                SELECT code
                FROM visit_plans
                WHERE code = %s AND session_code = %s
                FOR UPDATE
            """, (collection_code, session_code)).fetchone()

            if plan is None:
                raise LookupError("Visit plan not found.")

            connection.execute("""
                INSERT INTO visit_plan_items
                    (plan_code, exhibit_code, allocated_minutes)
                VALUES (%s, %s, %s)
            """, (
                collection_code,
                entry["exhibitCode"],
                entry["allocatedMinutes"]
            ))

    def edit(
        self,
        collection_code: str,
        session_code: str,
        item_code: str,
        entry: dict
    ) -> None:
        with psycopg.connect(self.url, connect_timeout=3) as connection:

            plan = connection.execute("""
                SELECT code
                FROM visit_plans
                WHERE code = %s AND session_code = %s
                FOR UPDATE
            """, (collection_code, session_code)).fetchone()

            if plan is None:
                raise LookupError("Visit plan not found.")

            result = connection.execute("""
                UPDATE visit_plan_items
                SET allocated_minutes = %s
                WHERE plan_code = %s AND exhibit_code = %s
            """, (
                entry["allocatedMinutes"],
                collection_code,
                item_code
            ))

            if result.rowcount == 0:
                raise LookupError("Exhibit is not in this visit plan.")

    def remove(
        self,
        collection_code: str,
        session_code: str,
        item_code: str
    ) -> None:
        with psycopg.connect(self.url, connect_timeout=3) as connection:

            plan = connection.execute("""
                SELECT code
                FROM visit_plans
                WHERE code = %s AND session_code = %s
                FOR UPDATE
            """, (collection_code, session_code)).fetchone()

            if plan is None:
                raise LookupError("Visit plan not found.")

            result = connection.execute("""
                DELETE FROM visit_plan_items
                WHERE plan_code = %s AND exhibit_code = %s
            """, (collection_code, item_code))

            if result.rowcount == 0:
                raise LookupError("Exhibit is not in this visit plan.")
