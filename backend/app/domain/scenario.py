"""Pure scenario business rules; no HTTP, database or other-layer imports."""
def validate_entry(entry: dict) -> None:
    # TODO: strict whole numbers, assigned field names and inclusive bounds.
    # Reuse for POST and PUT. Zero is valid in S15/S16; DELETE is separate.
    raise NotImplementedError("Implement assigned scenario validation")

def calculate_result(saved_entries: list[dict], stored_catalogue: list[dict]):
    # TODO: saved values + stored reference data, in scenario units.
    # Some scenarios sum allocations or add allowances rather than multiply.
    raise NotImplementedError("Implement assigned scenario calculation")
