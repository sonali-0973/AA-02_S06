# AA-02 scenario starter

## Project Overview

Runnable Python/PostgreSQL/JavaScript/Nginx bootstrap for any assigned S01-S20 scenario. It includes neutral catalogue connectivity and explicit TODO boundaries. It is not a completed assessment solution. TODO: enter the assigned scenario ID, title and application purpose.

## Group Members

TODO: record all three students' IDs, names and actual contributions here and in submission-manifest.yml. Replace its group and scenario placeholders before submission.

## Technology Stack

Python 3.14, FastAPI, psycopg, PostgreSQL 18, vanilla JavaScript and Nginx. Docker Compose v2 with `include` support is required. No Node build step is needed. Python dependencies are installed in the backend container.

## Setup Instructions

1. Install and start the class-approved Docker engine with Compose v2. Check `docker version` and `docker compose version`.
2. Open a terminal at this project root (the folder containing submission-manifest.yml).
3. Run `docker compose -f config/docker-compose.yml config` to verify resolved configuration.
4. Run the startup command below. Ports 8080 and 8000 must be free. Local development database credentials are in config/docker-compose.yml; do not use them for a public deployment.

The first startup initialises database/001-schema.sql and 002-seed.sql on a new Compose volume. Later edits to SQL files do not automatically update an existing database. Apply a reviewed migration, or use a fresh project name for a disposable development run. Do not remove a volume containing work you need.

## Run Instructions

```sh
docker compose -f config/docker-compose.yml up --build -d
docker compose -f config/docker-compose.yml ps
docker compose -f config/docker-compose.yml logs backend database
```

Open http://127.0.0.1:8080 and select **Check connection** and **Load bootstrap catalogue**. The first checks API-to-database connectivity; the second reads SAMPLE-001 from PostgreSQL. **Try collection TODO** deliberately reports SCENARIO_TODO (HTTP 501). Use the same-origin frontend URL for API calls so the Nginx proxy is exercised. API documentation is at http://127.0.0.1:8000/api/docs.

In Windows PowerShell, use `curl.exe` instead of `curl` to avoid the older alias.

```sh
curl http://127.0.0.1:8080/api/health
curl http://127.0.0.1:8080/api/catalogue
curl http://127.0.0.1:8000/api/catalogue/SAMPLE-001
docker compose -f config/docker-compose.yml exec -T database psql -U postgres -d scenario_starter -c "SELECT code, name FROM catalogue_items;"
docker compose -f config/docker-compose.yml down
```

`down` stops this project's services and keeps its database volume. Root docker-compose.yml and docker-compose.mac.yml include the same portable config for older command habits. Use one project name/config consistently; do not start multiple copies on the same ports.

## API Endpoints

| Method/path | Bootstrap behaviour |
| --- | --- |
| GET /api/health | Checks PostgreSQL; reports bootstrap scope |
| GET /api/catalogue | Reads neutral seed data |
| GET /api/catalogue/{item_code} | Reads one seed; unknown code is 404 |
| POST /api/collections | TODO: create or return session-owned collection (501) |
| GET /api/collections/{collection_code} | TODO: read owned saved entries/result (501) |
| POST /api/collections/{collection_code}/items | TODO: add validated entry (501) |
| PUT /api/collections/{collection_code}/items/{item_code} | TODO: edit validated entry (501) |
| DELETE /api/collections/{collection_code}/items/{item_code} | TODO: remove entry (501) |

Collection stubs require a non-empty X-Session-Code; missing/empty headers and malformed bodies receive 400. No collection identity, persistence, ownership enforcement or calculation is supplied by these stubs. Replace generic paths, DTOs, fields and seeds with your scenario's exact names. See [REQUIREMENTS.md](REQUIREMENTS.md) for adaptation points and all scenario families.

## Known Limitations

TODO: record actual limitations after implementation. The bootstrap has no completed scenario workflow, mutation logic, domain validation, result calculation or student evidence. Its mock session is not authentication, and a new page load creates a new code. It has no payment, checkout, hardware control, mapping or scheduling features. A startup smoke check does not prove the assigned scenario or its evidence is complete.

Required evidence templates are in evidence/. Fill every heading using actual success/error observations, a genuine issue/fix/retest and individual contributions. Acknowledge sources, libraries, examples and required AI use, including incorporated output and verification/modification. Supply screenshots, exports or logs only when your evidence references them. The brief's malformed contribution link is interpreted as the local evidence/contribution-evidence.md path, consistent with its Required Evidence Files and Submission Requirements.

Complete the manifest and actual evidence; the presence of templates alone does not meet assessment expectations. Follow [INSTRUCTION.md](INSTRUCTION.md) for the full numbered workflow from group formation through Canvas upload.

## Local submission checker

Install the small checker dependency on the host: `python -m pip install -r config/checker-requirements.txt`. Python 3.10 or newer can run the checker independently of the Python 3.14 application container. Run from the project root:

```sh
python check_submission.py .
python check_submission.py /path/to/128-353-AA2-YourGroupID.zip
```

The ten C01-C10 lines correspond to the brief's ten submission artefact bullets. ZIP input adds A01 format and A02 filename/group matching. Every line is TRUE or FALSE with an actionable failure message. Exit status is 0 when all local checks pass and 1 when any check fails. ZIPs can contain the project at the archive root or within one enclosing project folder. The checker reads files only and never imports or executes submitted application code, startup commands or evidence scripts.

The untouched starter reports **C01-C10 all FALSE**. C01 checks required manifest fields and obvious placeholders. C02 and C07-C09 require every specified README/evidence heading to contain substantive, non-placeholder content; headings alone do not pass. C03-C05 require source or data beyond the unchanged distributed bootstrap. C06 requires configuration files plus a documented, actual setup/configuration verification result in the README Setup Instructions. A working configuration may be reused unchanged.

C10 requires completed evidence sections and checks referenced local Markdown links/images, reference-link definitions, HTML src/href attributes and single-backtick asset paths ending in common evidence extensions. Use links relative to each evidence file, for example `[Observed log](assets/request.log)` for `evidence/assets/request.log`. Angle brackets support linked filenames containing spaces. Remote web URLs and in-document fragments are not downloaded or verified. Local references must stay inside the submission; ZIP entries must use safe unique relative paths and cannot be symbolic links. Evidence can pass with **zero attachments** when its completed text has no local asset references.

These are local readiness heuristics based on file content and bundled bootstrap fingerprints. A changed file or TRUE result does not prove working integration, correct scenario calculations, complete or authentic observations, accurate contributions, source/AI acknowledgement quality, or an assessment grade. The checker never runs submitted code. Canvas upload and the Course Leader's confirmed deadline remain manual steps outside the automated results.

### Local submission checker details

The local submission checker `check_submission.py` uses these criteria:

| Check | Returns TRUE when |
|---|---|
| C01 Manifest | YAML is valid, required fields and artefact paths are correct, identity placeholders are replaced, and URLs have valid HTTP(S) form. |
| C02 README | Every required heading exists and contains non-empty, non-placeholder text. |
| C03 Frontend | Recognised, non-empty source files exist, and at least one is added or changed from the distributed starter. |
| C04 Backend | Same rule as C03, applied to backend/. |
| C05 Database | Recognised, non-empty data/schema/model files exist, with an addition or change from the starter. |
| C06 Configuration | Configuration files exist, and README Setup Instructions contains no placeholders and a verification word such as `tested`, `verified` or `passed`. Existing configuration may be reused. |
| C07 Integration evidence | Every required heading contains non-empty, non-placeholder text. |
| C08 Testing/debugging evidence | Same section-completion rule as C07. |
| C09 Contribution evidence | Same section-completion rule as C07. |
| C10 Referenced assets | All three evidence documents pass their section checks, and every recognised local asset reference resolves to a readable file inside the submission. Attachments are optional when evidence is inline. |

For ZIP input, it additionally checks:

- A01: readable ZIP, valid file integrity and safe archive structure.
- A02: filename exactly matches `128-353-AA2-<group.id>.zip`.

Placeholder detection includes TODO, TBD, FIXME and known template phrases. There is no minimum word count. Source comparisons ignore line-ending differences.

These are local heuristics. A changed file does not prove implemented functionality, and filled evidence sections do not prove authentic evidence. The checker does not run the application, validate scenario calculations, verify Canvas submission or award grades.