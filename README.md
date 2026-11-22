# Museum Group Visit Planner (AA-02, S06)

## Project Overview

Scenario S06, Museum group visit planner, for course 128-353. A group organiser browses fictional museum exhibits, checks each exhibit's theme and suggested visit time, and chooses stops with an allocated number of minutes. The seeded exhibit catalogue is kept separate from the saved visit plan. The plan belongs to one anonymous mock session, and its allocations can be changed or removed. The backend calculates the total visit minutes as the sum of the saved allocations. Suggested times are reference information only.

The system has three connected services: a vanilla JavaScript frontend served by Nginx, a FastAPI backend and a PostgreSQL database, all started with Docker Compose. The project was built by the group on 21 November 2026.

## Group Members

| Student ID | Name | Contribution |
| --- | --- | --- |
| 6704864030 | Zin Nwe Moe | Backend: FastAPI routes, application service, validation, PostgreSQL access and the total calculation |
| 6704864006 | Thura Hein Thant | Frontend: exhibit browsing and details, allocation controls, saved-plan display, validation feedback and request log |
| 6704864023 | Min Khant Zaw | Database: schema for exhibits, visit plans and plan items, and the exhibit seed data |

All three members worked together on integration and ran the evidence cases. Full details are in the manifest and in evidence/contribution-evidence.md.

## Technology Stack

Python 3.14, FastAPI, Pydantic, psycopg, PostgreSQL 18, vanilla JavaScript (ES modules) and Nginx. Docker Compose v2 with `include` support is required. No Node build step is needed, and Python dependencies are installed in the backend container.

## Setup Instructions

1. Install and start Docker with Compose v2, and run `docker version` and `docker compose version`.
2. Open a terminal at the project root, the folder that contains submission-manifest.yml.
3. Run `docker compose -f config/docker-compose.yml config` to print the resolved configuration.
4. Make sure ports 8080 (frontend) and 8000 (backend) are free, then start the stack with the command in Run Instructions.

Verification result (21 November 2026): we verified that Docker Compose ran on our machines (Docker Compose 5.7.0 on the machine used for the evidence runs) and confirmed that `docker compose -f config/docker-compose.yml config` printed the resolved configuration for the database, backend and frontend services without errors. We checked that ports 8080 and 8000 were free, and observed all three services running with `docker compose -f config/docker-compose.yml ps` after `up --build -d --wait`. [VERIFY each claim]

The first startup runs database/001-schema.sql and database/002-seed.sql on a new Compose volume only. Later edits to the SQL files do not update an existing volume. We hit this during integration: the API returned `SERVICE_UNAVAILABLE` because the database volume had been created from the starter schema. We fixed it with `docker compose -f config/docker-compose.yml down -v` and a rebuild, and tested that `GET /api/exhibits` then returned six exhibits. The `-v` option deletes the local database data, which is only seed data and plans created during testing.

## Run Instructions

```sh
docker compose -f config/docker-compose.yml up --build -d --wait
docker compose -f config/docker-compose.yml ps
docker compose -f config/docker-compose.yml logs backend database
```

Open http://127.0.0.1:8080. The exhibit list loads, and selecting an exhibit shows its theme and suggested time. Enter minutes and choose Add to plan to add a stop. Each saved stop has a Minutes box with Save minutes, and a Remove button. The Total visit time shown is the backend's total. The Request log under the plan lists each request with its method, path, status, session header, body and response. Use the same-origin frontend URL so the Nginx proxy to the API is exercised. API documentation is at http://127.0.0.1:8000/api/docs.

To check the API directly, use one session code for every plan request. In PowerShell use `curl.exe` instead of `curl`.

```sh
curl http://127.0.0.1:8080/api/exhibits
curl -X POST http://127.0.0.1:8080/api/visit-plans -H "X-Session-Code: demo-session"
curl -X POST http://127.0.0.1:8080/api/visit-plans/PLAN_CODE/items -H "X-Session-Code: demo-session" -H "Content-Type: application/json" -d '{"exhibitCode":"EXH-001","allocatedMinutes":15}'
curl http://127.0.0.1:8080/api/visit-plans/PLAN_CODE -H "X-Session-Code: demo-session"
docker compose -f config/docker-compose.yml exec -T database psql -U postgres -d scenario_starter -c "SELECT * FROM visit_plan_items;"
docker compose -f config/docker-compose.yml down
```

Replace PLAN_CODE with the `planCode` returned by the POST to /api/visit-plans. The `down` command stops the services and keeps the database volume.

## API Endpoints

All plan requests need a non-empty `X-Session-Code` header. The catalogue routes do not.

| Method and path | Purpose |
| --- | --- |
| GET /api/health | Checks the API and database connection |
| GET /api/exhibits | Returns `items`, each with `code`, `name`, `theme`, `suggestedMinutes` |
| GET /api/exhibits/{exhibitCode} | Returns one exhibit; an unknown code gives 404 |
| POST /api/visit-plans | Creates or returns the session's plan: `planCode`, `items`, `totalVisitMinutes` |
| GET /api/visit-plans/{planCode} | Returns saved stops (`exhibitCode`, `name`, `theme`, `suggestedMinutes`, `allocatedMinutes`) and `totalVisitMinutes` |
| POST /api/visit-plans/{planCode}/items | Body `{"exhibitCode","allocatedMinutes"}`; adds a stop |
| PUT /api/visit-plans/{planCode}/items/{exhibitCode} | Body `{"allocatedMinutes"}`; changes an allocation |
| DELETE /api/visit-plans/{planCode}/items/{exhibitCode} | Removes a stop; the exhibit stays in the catalogue |

`allocatedMinutes` must be a whole number from 5 to 60 inclusive. A value outside that range or of the wrong type is rejected with status 400 and the body `{"error_code": "INVALID_REQUEST", "message": "Check request fields and X-Session-Code."}`, and the saved stops and total are left unchanged. A plan or stop that does not belong to the session or does not exist gives 404, and a database failure gives 503. Successful create, add, edit and remove calls return 200 with the updated plan. The frontend calls GET on the plan after every add, edit or remove and shows only the returned values.

## Known Limitations

The mock session code is not authentication. The frontend creates a new code on every page load, so a reload starts a new plan, and persistence across reloads is outside this scenario. Every validation failure returns the same generic 400 message, which does not state the 5 to 60 minute range. The seed data is applied only when the database volume is first created, so changing the SQL files needs `down -v` and a rebuild, which deletes local data. The catalogue is small and fictional, and the tool records chosen allocations only; it does not build an automatic schedule. The request log on the page is held in memory and clears when the page is reloaded. Our evidence was gathered with the page and with curl against the Docker setup on [our machines; VERIFY], and we have not tested other browsers or any deployment outside local Docker.

Evidence files are in evidence/. Follow [INSTRUCTION.md](INSTRUCTION.md) for the full submission workflow.

## Local submission checker

Install the dependency with `python -m pip install -r config/checker-requirements.txt`, then run `python check_submission.py .` from the project root. The checker only reads files and does not run the application.