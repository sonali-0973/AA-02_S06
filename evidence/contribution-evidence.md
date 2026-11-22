# Contribution Evidence

## Contribution Summary

Our group of three built the S06 Museum group visit planner together on 21 November 2026. The frontend (HTML, CSS and JavaScript served by Nginx) lets an organiser browse fictional exhibits, add stops with chosen allocated minutes, edit or remove them, and see the saved plan with a server-calculated total. The backend (Python, FastAPI) provides the catalogue and session-plan routes and validates allocations from 5 to 60 whole minutes. The PostgreSQL database stores exhibits, visit plans and plan items. Docker Compose connects the three services. We agreed the endpoints and field names from the S06 scenario file and integrated our work in the shared repository.

## Individual Contributions

All three of us worked on the project together on 21 November 2026, and each of us ran the evidence cases and recorded the results.

**Zin Nwe Moe (6704864030): Backend.** Implemented the FastAPI application service, business logic and input validation for visit plans. Built the endpoints to list exhibits, create or return a visit plan, add an exhibit, update allocated minutes and delete an exhibit. Connected the API to PostgreSQL with parameterised SQL queries and session-based access, and calculated the total visit time from saved allocations. Files: `backend/app/presentation/api.py`, `backend/app/domain/scenario.py`, `backend/app/application/service.py`, `backend/app/infrastructure/postgres.py`. Date: 21 November 2026.

**Thura Hein Thant (6704864006): Frontend.** Built the exhibit list and detail view (theme and suggested time), the add, save-minutes and remove controls, and the saved-plan display with total minutes and validation error feedback. Wrote an API wrapper for the S06 routes, sent the same `X-Session-Code` header on every plan request, and queued all requests through the starter's action queue. After each add, edit or remove the page re-fetches the saved plan and renders only what the server returned, and it never calculates totals in JavaScript. Updated `http.js` to log each request with its method, path, status and response for evidence capture. Files: `frontend/index.html`, `frontend/assets/styles/main.css`, `frontend/scripts/index.js`, `frontend/scripts/api.js`, `frontend/scripts/http.js`. Date: 21 November 2026.

**Min Khant Zaw (6704864023): Database.** Designed the schema in `database/001-schema.sql`: tables `exhibits`, `visit_plans` and `visit_plan_items`, with primary and foreign keys, a CHECK limiting `allocated_minutes` to 5 to 60, and an index on plan items. Wrote `database/002-seed.sql` with six fictional exhibits, including EXH-001 (20 minutes) and EXH-002 (30 minutes). Date: 21 November 2026.

**Configuration and integration:** all three of us worked together to start the frontend, API and database services with Docker Compose, ran the four S06 evidence cases with one session code, and recorded the issues, fixes and retests described in the testing evidence.

## Research or Technology Decisions

- **No client-side range check:** the frontend sends whatever the user types, so the server's 5 to 60 validation is what gets tested and shown. This keeps the evidence case for an invalid value genuine.
- **Re-fetch after every change:** the page calls GET on the plan after each add, edit or remove, so totals always come from the server.
- **Normalising response fields in one place:** the `norm*` functions in `api.js` map the backend's JSON to what the page displays, so a naming change needs one edit.
- **Backend technology:** we used FastAPI, Pydantic and psycopg, which the starter project used. Request models use `StrictInt` with a 5 to 60 limit, so strings, decimals and out-of-range values are rejected at the API boundary. The business rule is also in `domain/scenario.py`, which has no HTTP or database dependencies, so it can be tested alone. We kept the starter's split into presentation, application, domain and infrastructure layers, so routes, rules and SQL stay in separate files.
- **Database design:** the exhibit catalogue is a separate table from the visit plans, so removing a stop never touches the seeded exhibits. `visit_plans.session_code` is `UNIQUE`, so one session has one plan, which is what create-or-return needs. The composite key `(plan_code, exhibit_code)` stops the same exhibit being added twice to a plan. Foreign keys tie every item to a real plan and exhibit, and a `CHECK` on `allocated_minutes` enforces 5 to 60 in the database as well as in the API.
- 
## Academic Integrity and Source Acknowledgement

**Sources and libraries:** the starter code supplied for the assessment (Nginx config, `http.js`, `action-queue.js`, FastAPI project structure); FastAPI, Pydantic, psycopg and PostgreSQL 18; Docker and Docker Compose.

**AI use (all three members):** we used two AI tools, Claude (Anthropic) and ChatGPT (OpenAI), on 21 November 2026.
- **Purpose:** to draft and revise code, to explain error messages from Docker, Nginx and the backend, and to draft wording for the manifest and these evidence files.
- **Outputs incorporated:** the frontend files drafted with Claude and then reviewed and edited by Thura Hein Thant .For the backend, Zin Nwe Moe used ChatGPT to review the FastAPI application service. We also used both tools' explanations of the `host not found in upstream "backend"` Nginx error and the `relation "exhibits" does not exist` database error, and their suggested Docker commands. We also used these tools to help with their backend and database work.
- **Changes we made:** we adapted the generated suggestions to our actual project architecture, S06 scenario requirements, database relationships and API responses. For the backend, we reviewed and adjusted the service logic to ensure that visit-plan operations used the correct session code, validated exhibit references and allocated minutes, and calculated totals using saved database records. For the frontend, we changed exhibit list handling to match the items key returned by the backend and updated error handling to read FastAPI's detail field. We also rewrote the AI-drafted manifest and evidence wording to accurately describe our actual contributions.
**Verification:** we ran the application with Docker Compose, compared the page's field names with the real API responses, and checked the four S06 evidence cases against the saved API responses, request logs and database rows listed in the evidence files. We did not rely on AI output without testing it.
**Issues found while integrating:**
- The `frontend` container stopped with `host not found in upstream "backend"` because Nginx could not resolve the backend at startup. We fixed it by recreating the containers with `docker compose -f config/docker-compose.yml down` and `up --build -d --wait`.
- The browser showed `SERVICE_UNAVAILABLE`. The backend log reported `relation "exhibits" does not exist`, which showed the database had been created from the starter schema, because Postgres only runs the schema and seed scripts when the volume is first created. We reset the volume with `docker compose -f config/docker-compose.yml down -v` and rebuilt. After the rebuild, `GET /api/exhibits` returned all six seeded exhibits (EXH-001 to EXH-006) and the page loaded the exhibit list.
 