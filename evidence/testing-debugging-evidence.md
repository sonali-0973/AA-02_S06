# Testing Debugging Evidence

## API Request Evidence

All requests were made against the running Docker Compose stack through Nginx at http://127.0.0.1:8080 on 21 November 2026, using one mock session code in `X-Session-Code` for every visit-plan request.

**Failing request (before the fix).** `GET /api/exhibits` did not return the exhibit catalogue. The backend handled it as an unhandled exception and the starter's error handler converted it to 503 with `{"error_code": "SERVICE_UNAVAILABLE", "message": "Check API/database logs."}`. The page showed this text as "Could not start: Check API/database logs. (SERVICE_UNAVAILABLE)".

**Passing requests (after the fix).** From the page's request log (11:39 to 11:40 AM):

| Request | Status | Observed |
|---|---|---|
| `GET /api/exhibits` | 200 | `items` list of six exhibits, EXH-001 to EXH-006 |
| `GET /api/exhibits/EXH-001` | 200 | The Golden Kingdoms, Ancient Civilisations, 20 suggested minutes |
| `POST /api/visit-plans` | 200 | `planCode` `PLAN-5E10FFBFB01B`, empty `items`, `totalVisitMinutes` 0 |
| `POST .../items` `{"exhibitCode":"EXH-001","allocatedMinutes":20}` | 200 | one item, `totalVisitMinutes` 20 |
| `PUT .../items/EXH-001` `{"allocatedMinutes":10}` | 200 | `allocatedMinutes` 10, `totalVisitMinutes` 10 |
| `DELETE .../items/EXH-001` | 200 | empty `items`, `totalVisitMinutes` 0 |

**Validation request.** An allocation below 5 (for example 4) was rejected with status 400 and the body `{"error_code": "INVALID_REQUEST", "message": "Check request fields and X-Session-Code."}`. The saved plan and total were unchanged afterwards.

**Evidence cases.** The four S06 cases (15 and 20 minutes added for a total of 35, changed to 25 for a total of 45, EXH-002 removed for a total of 25, and 4 rejected with 25 retained) were run with one session code. After case 1 the database held EXH-001 at 15 and EXH-002 at 20 in `visit_plan_items`. 

## Browser or Network Evidence

Observed in the browser at http://127.0.0.1:8080:

- **Before the fix:** the status line read "Could not start: Check API/database logs. (SERVICE_UNAVAILABLE)", the Exhibits card was empty and the plan card showed "not created yet" with a total of 0 min.
- **After the fix:** the Exhibits card listed six exhibits and the plan card showed a plan code and a total of 0 min until stops were added.
- **Invalid allocation:** entering a value below 5 in the Add to plan box showed a red error box reading "Adding stop failed: Check request fields and X-Session-Code. (INVALID_REQUEST)" and the status line "Nothing was changed." The browser console reported `400 (Bad Request)` for that request. Editing a saved allocation to 4 is expected to show "Saving minutes failed: ..." with the same message.
- **Request log:** the page's Request log records the time, method, path, status, session header, body and response of each request, and showed the same session code on every plan request.

## Log or Console Evidence

**Backend log (before the fix),** from `docker compose -f config/docker-compose.yml logs backend --tail 30`:

```
File "/backend/app/presentation/api.py", line 53, in get_exhibits
    "items": service.catalogue()
File "/backend/app/infrastructure/postgres.py", line 33, in catalogue
    rows = connection.execute """
psycopg.errors.UndefinedTable: relation "exhibits" does not exist
LINE 7:                 FROM exhibits
```

**Frontend container log,** from `docker compose -f config/docker-compose.yml logs frontend --tail 20`:

```
[emerg] 1#1: host not found in upstream "backend" in /etc/nginx/conf.d/default.conf:6
nginx: [emerg] host not found in upstream "backend" in /etc/nginx/conf.d/default.conf:6
```

**Earlier database log.** The first database start reported `CREATE TABLE` three times and `INSERT 0 1`, which is the starter's schema and seed, so our own schema had not been applied to that volume.

**Browser console:** `400 (Bad Request)` for the rejected allocation request.

## Issue Found

**Issue 1: the exhibit catalogue failed with 503 (main issue).**

- **Steps to reproduce:** run `docker compose -f config/docker-compose.yml up --build -d --wait` on a machine that already holds the database volume from the starter, then open http://127.0.0.1:8080.
- **Expected:** `GET /api/exhibits` returns six exhibits and the page lists them.
- **Actual:** the page showed "Could not start: Check API/database logs. (SERVICE_UNAVAILABLE)". The backend log showed `psycopg.errors.UndefinedTable: relation "exhibits" does not exist`.
- **Cause:** PostgreSQL runs the scripts in `docker-entrypoint-initdb.d` only when the data volume is first created. The volume had been created from the starter schema, so our `exhibits`, `visit_plans` and `visit_plan_items` tables, and the six seeded exhibits, were never applied.

**Issue 2: the frontend container kept stopping.**

- **Steps to reproduce:** start the stack with Docker Compose, then check `docker compose -f config/docker-compose.yml ps`.
- **Expected:** `frontend` stays running and serves the page.
- **Actual:** only the backend and database were running, and opening port 8080 showed no page. The frontend log reported `host not found in upstream "backend"` at the Nginx config's line 6.
- **Observation:** the compose file already put `frontend` on the same default network as `backend`, with `depends_on` for `backend`, so the fault was not a missing configuration line.

**Observation: the validation message is generic.** The backend's request-validation handler returns the same text for every invalid request, including a wrong allocation, so the message does not mention the 5 to 60 range.

## Fix Applied

**Issue 1:** on 21 November 2026 we removed the stale database volume and rebuilt, so the database container re-ran `001-schema.sql` and `002-seed.sql`:

```sh
docker compose -f config/docker-compose.yml down -v
docker compose -f config/docker-compose.yml up --build -d --wait
```

No application code was changed for this issue.

**Issue 2:**  recreating the containers with `docker compose -f config/docker-compose.yml down` and `up --build -d --wait`, or restarting Docker Desktop.

**Validation message:** we recorded it as a known limitation in the README rather than changing the backend. 

## Retest Evidence

**Issue 1:** after the volume reset and rebuild, `GET /api/exhibits` returned 200 with the six seeded exhibits (EXH-001 to EXH-006), and the page listed them. We then ran the add, edit and remove flow, and every request returned 200 with the saved plan re-read by a GET, as shown in the API request table above. The backend log no longer showed the `UndefinedTable` error. 

**Issue 2:** after the fix, `docker compose -f config/docker-compose.yml ps` showed `frontend`, `backend` and `database` all running, and http://127.0.0.1:8080 served the page.

**Repeatability:** a reset and rebuild with the two commands above gives a working stack from the submitted files.