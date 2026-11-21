
"""Pure scenario business rules for S06: Museum Group Visit Planner.

This module contains no HTTP or database dependencies.
"""

MIN_ALLOCATED_MINUTES = 5
MAX_ALLOCATED_MINUTES = 60


class InvalidAllocation(ValueError):
    """Raised when an exhibit's allocated time is invalid."""


def validate_entry(entry: dict) -> None:
    """Validate the allocated minutes for an exhibit.

    The value must be a whole integer between 5 and 60 inclusive.
    Booleans, floats, strings and missing values are rejected.
    """
    if not isinstance(entry, dict):
        raise InvalidAllocation("Entry must be an object.")

    value = entry.get("allocatedMinutes")

    if isinstance(value, bool) or not isinstance(value, int):
        raise InvalidAllocation(
            "allocatedMinutes must be a whole number."
        )

    if not MIN_ALLOCATED_MINUTES <= value <= MAX_ALLOCATED_MINUTES:
        raise InvalidAllocation(
            "allocatedMinutes must be between 5 and 60 inclusive."
        )


def calculate_result(
    saved_entries: list[dict],
    stored_catalogue: list[dict]
) -> int:
    """Calculate total visit time using saved exhibit allocations.

    Catalogue suggested times are intentionally ignored.
    """
    total_minutes = 0

    for entry in saved_entries:
        validate_entry(entry)
        total_minutes += entry["allocatedMinutes"]

    return total_minutes
