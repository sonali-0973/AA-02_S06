# Integration Evidence

## Integrated Workflow

Date: 21 November 2026. **Stack:** Nginx frontend, FastAPI backend and PostgreSQL database started together with `docker compose -f config/docker-compose.yml up --build -d --wait`, opened at http://127.0.0.1:8080.

The page creates one mock session code (a UUID generated when the page loads) and sends it in `X-Session-Code` on every visit-plan request. The workflow is:

1. On load, the page calls `GET /api/exhibits` and shows the list.
2. Clicking an exhibit calls `GET /api/exhibits/{exhibitCode}` and shows its theme and suggested visit time.
3. The page calls `POST /api/visit-plans` and keeps the returned `planCode`.
4. Adding a stop calls `POST /api/visit-plans/{planCode}/items`, then `GET /api/visit-plans/{planCode}`.
5. Saving new minutes calls `PUT /api/visit-plans/{planCode}/items/{exhibitCode}`, then the same GET.
6. Removing a stop calls `DELETE /api/visit-plans/{planCode}/items/{exhibitCode}`, then the same GET.

All plan requests go through the action queue, so they run one at a time. The page draws the plan only from the GET response and never adds up minutes itself. The page also keeps a request log that records each request's time, method, path, status, session header, body and response. Excerpts from it are quoted in the sections below.

## Frontend Evidence

Observed in the browser against the running stack on 21 November 2026:

- The Exhibits card listed the six seeded exhibits, EXH-001 to EXH-006, each with its code and suggested minutes.
- Selecting EXH-001 showed "The Golden Kingdoms", theme "Ancient Civilisations" and suggested time 20 minutes, with a minutes box and an Add to plan button.
- After "Add to plan" the Your visit plan card listed the stop with its saved allocation and the server's total in the Total visit time bar.
- Each stop had a Minutes box with Save minutes, and a Remove button. After Remove the stop left the plan card but stayed in the exhibit list.
- For the brief's evidence cases: after adding EXH-001 at 15 and EXH-002 at 20 the total bar read 35 min; after changing EXH-001 to 25 it read 45 min; after removing EXH-002 it showed EXH-001 at 25 min and a total of 25 min; after entering 4 the page showed an error box and kept 25 min. 

The same session code, `4c62ede7-951b-46bf-879f-4c1bb9acdb76` in the logged run, appeared in every plan request. The catalogue requests carry no session header.

## Backend API Evidence

General API Request-Log Test Run — From the page's request log on 21 November 2026 (11:39 to 11:40 AM), the API responded as follows:

| Request | Status | Response |
|---|---|---|
| `GET /api/exhibits` | 200 | `items` list of six exhibits with `code`, `name`, `theme`, `suggestedMinutes` |
| `GET /api/exhibits/EXH-001` | 200 | `code` EXH-001, `name` The Golden Kingdoms, `theme` Ancient Civilisations, `suggestedMinutes` 20 |
| `POST /api/visit-plans` | 200 | `planCode` `PLAN-5E10FFBFB01B`, empty `items`, `totalVisitMinutes` 0 |
| `POST .../items` with `{"exhibitCode":"EXH-001","allocatedMinutes":20}` | 200 | plan with one item, `allocatedMinutes` 20, `totalVisitMinutes` 20 |
| `PUT .../items/EXH-001` with `{"allocatedMinutes":10}` | 200 | plan with `allocatedMinutes` 10, `totalVisitMinutes` 10 |
| `DELETE .../items/EXH-001` | 200 | plan with empty `items`, `totalVisitMinutes` 0 |
| `POST .../items` with `allocatedMinutes` below 5 | 400 | `{"error_code": "INVALID_REQUEST", "message": "Check request fields and X-Session-Code."}` |

After each successful change, a subsequent `GET /api/visit-plans/{planCode}` returned the same saved state as the corresponding mutation response. Each plan item included the exhibit's `name`, `theme` and `suggestedMinutes` beside the saved `allocatedMinutes`, and also included the updated `totalVisitMinutes`. The create, add, edit, and delete requests all returned HTTP 200. An allocation below the minimum of 5 minutes was rejected with `HTTP 400` and an `INVALID_REQUEST` response.

### Separate Test Run: Four S06 Evidence Cases

The following four cases were executed separately using one session code and the values specified in the S06 brief:

| Case | Request | Expected | Observed |
|---|---|---|---|
| 1 | Add EXH-001 at 15, EXH-002 at 20, then GET plan | two items, total 35 | Two items with allocations 15 and 20 and `totalVisitMinutes` 35. |
| 2 | `PUT {"allocatedMinutes":25}` on EXH-001, then GET | EXH-001 at 25, total 45 | EXH-001 at 25 and `totalVisitMinutes` 45.  |
| 3 | `DELETE` EXH-002, then GET | EXH-001 at 25, total 25 | EXH-001 still at 25, `totalVisitMinutes` 25, EXH-002 still in the catalogue. |
| 4 | `PUT {"allocatedMinutes":4}` on EXH-001, then GET | 4xx, plan unchanged | 400 with the body above; the GET afterwards showed EXH-001 at 25 and total 25. |

## Database Evidence

The schema in `database/001-schema.sql` creates `exhibits`, `visit_plans` and `visit_plan_items`, and `database/002-seed.sql` seeds six exhibits. On our first run the backend failed with `relation "exhibits" does not exist`, because the database volume had been created from the starter schema and PostgreSQL only runs the schema and seed scripts when the volume is first created. We reset the volume with `docker compose -f config/docker-compose.yml down -v` and rebuilt, after which `GET /api/exhibits` returned all six exhibits.

The saved plan state also matches the database. After the DELETE in the logged run, the GET returned no items, so the row had been removed from `visit_plan_items`, while the catalogue still listed EXH-001. We also read the saved rows directly from PostgreSQL:

```sh
docker compose -f config/docker-compose.yml exec database psql -U postgres -d scenario_starter -c "SELECT * FROM visit_plan_items;"
```

Output after the four cases:     
 plan_code     | exhibit_code | allocated_minutes 
-------------------+--------------+-------------------
 PLAN-5E10FFBFB01B | EXH-002      |                25
(1 row). 

## Success Case

On 21 November 2026, with one session code, the page's request log showed this sequence for plan `PLAN-5E10FFBFB01B`:

1. `POST /api/visit-plans/PLAN-5E10FFBFB01B/items` with `{"exhibitCode":"EXH-001","allocatedMinutes":20}` returned 200, and the next `GET` returned one item with `allocatedMinutes` 20 and `totalVisitMinutes` 20.
2. `PUT .../items/EXH-001` with `{"allocatedMinutes":10}` returned 200, and the next `GET` showed 10 and a total of 10.
3. `DELETE .../items/EXH-001` returned 200, and the next `GET` showed no items and a total of 0.

At each step the page showed the same values as the GET response.For the separate S06 evidence test run, adding EXH-001 at 15 minutes and EXH-002 at 20 minutes produced a total of 35 minutes. Updating EXH-001 to 25 minutes produced a total of 45 minutes. Removing EXH-002 left EXH-001 at 25 minutes, with a total of 25 minutes. [VERIFY]

## Error or Empty-Data Case

We sent allocations below the allowed minimum of 5 minutes to the API in two ways: a `POST /api/visit-plans/{planCode}/items` from the Add to plan box, and a `PUT /api/visit-plans/{planCode}/items/EXH-001` with `{"allocatedMinutes":4}` from the Save minutes box.

**Add (POST) with an out-of-range value**
- **API response:** status 400 Bad Request,  with the body `{"error_code": "INVALID_REQUEST", "message": "Check request fields and X-Session-Code."}`. This is the starter's request-validation handler, which the 5 to 60 check on `allocatedMinutes` triggers.
- **Browser feedback:** the page showed a red error box reading "Adding stop failed: Check request fields and X-Session-Code. (INVALID_REQUEST)", and the status line "Nothing was changed."
- **State afterwards:** the plan was re-read with a GET and showed the same stops and total as before the attempt.

**Edit (PUT) with `{"allocatedMinutes":4}` on EXH-001** (case 4)
- **API response:** status 400 Bad Request with the same body, `{"error_code": "INVALID_REQUEST", "message": "Check request fields and X-Session-Code."}`. [VERIFY]
- **Browser feedback:** the page showed a red error box reading "Saving minutes failed: Check request fields and X-Session-Code. (INVALID_REQUEST)" and the status line "Nothing was changed." [VERIFY]
- **State afterwards:** the GET that followed returned EXH-001 at 25 minutes and a total of 25, and the page showed the same saved values.

Empty plan: when a session's plan has no stops, the page shows "No stops yet. Add an exhibit from the list." and a total of 0 min, which matches the empty `items` and `totalVisitMinutes` 0 returned by the API.