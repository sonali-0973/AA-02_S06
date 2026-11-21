-- S06 Museum group visit planner schema
CREATE TABLE exhibits (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    theme TEXT NOT NULL,
    suggested_minutes INTEGER NOT NULL CHECK (suggested_minutes > 0)
);

CREATE TABLE visit_plans (
    code TEXT PRIMARY KEY,
    session_code TEXT NOT NULL UNIQUE
);

CREATE TABLE visit_plan_items (
    plan_code TEXT NOT NULL REFERENCES visit_plans(code),
    exhibit_code TEXT NOT NULL REFERENCES exhibits(code),
    allocated_minutes INTEGER NOT NULL CHECK (allocated_minutes BETWEEN 5 AND 60),
    PRIMARY KEY (plan_code, exhibit_code)
);
-- DELETE removes only a plan item, never an exhibit.