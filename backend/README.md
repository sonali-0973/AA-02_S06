# Backend
Run through Compose from the project root as described in README.md. The container installs pyproject.toml and runs `uvicorn app.main:app --host 0.0.0.0 --port 8000` from /backend.

Dependency direction: presentation -> application -> domain; application -> infrastructure. Domain and infrastructure import no other project layer. Application adapters implement domain ports; the composition root wires the service. External database access goes through DataPort. Domain scenario.py owns business validation and calculations. HTTP routes contain no business logic.

Health and catalogue access work with PostgreSQL. Collection routes deliberately return 501 after header/body checks. TODO: implement CollectionPort, transactional ownership checks and domain rules, scenario request/response models, error handling, then rename the generic route and JSON names to the assigned contract. A missing/empty session header is 400. A session marker is not authentication. Avoid exposing another session's entries or modifying state on validation failure.
