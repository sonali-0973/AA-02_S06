-- Neutral bootstrap schema: extend/rename fields and constraints for your scenario.
CREATE TABLE catalogue_items (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    details JSONB NOT NULL DEFAULT '{}'
);
CREATE TABLE collections (
    code TEXT PRIMARY KEY,
    session_code TEXT NOT NULL UNIQUE
);
CREATE TABLE collection_entries (
    collection_code TEXT NOT NULL REFERENCES collections(code),
    item_code TEXT NOT NULL REFERENCES catalogue_items(code),
    -- TODO: scenario-specific field, strict whole number and inclusive bounds.
    entry_value INTEGER NOT NULL,
    PRIMARY KEY (collection_code, item_code)
);
-- Do not assume zero removes an entry; DELETE is separate.
