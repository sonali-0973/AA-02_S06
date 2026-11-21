# Scenario adaptation boundaries

The accepted scenario file and assessment brief govern the implementation. This bootstrap provides a running connection path, not scenario answers. Read the assigned file in full before editing.

## Common workflow

Rename the neutral catalogue and collection routes/fields to the assigned contract. Seed the required catalogue independently of editable entries. Implement create-or-return for one mock session, retain the returned collection code, and send X-Session-Code on every collection request. Scope every read and mutation by both session and collection identity; do not disclose another session's contents. Save identity and entries in PostgreSQL. Use parameterised SQL and transactions. Catalogue deletion is outside the collection DELETE operation.

Implement strict whole-number validation with the assigned inclusive bounds for both POST and PUT, rejecting fractional values and booleans without silently coercing them. Invalid mutations must return suitable 4xx responses and leave saved entries/results unchanged. Choose and document appropriate missing-code and ownership errors. DELETE removes the entry; never repurpose zero as deletion. Re-read authoritative state after mutations and render server-calculated results/errors in the browser. Keep session reads/writes ordered with action-queue.js. Reload persistence is outside the accepted scenarios.

## Layers and TODO files

- frontend/scripts/index.js: replace bootstrap controls, retain collection identity, implement browse/details/add/edit/remove and display server results.
- backend/app/presentation/api.py: scenario route names and typed request/response translation only.
- backend/app/application/service.py: implement CollectionPort adapters, ownership orchestration, persistence and domain calls.
- backend/app/domain/ports.py: I/O contracts; domain/scenario.py: pure business validation/calculation.
- backend/app/infrastructure/postgres.py: replaceable driver with parameterised SQL and transaction boundaries; no dependencies on other project layers.
- database/: scenario seeds, reference fields, saved field and bounds. Use exact decimal types where needed (money/area), not binary floating-point rounding assumptions.
- config/: repeatable startup and proxy configuration. Update manifest URLs/commands if configuration changes.

Project dependency direction is presentation -> application -> domain, with application -> infrastructure. External database access uses domain ports implemented in application adapters. Domain and infrastructure import no other project layers; main.py is the composition root. No circular imports or business calculations in routes/JavaScript.

## Compatibility map: all twenty scenarios

Each row requires scenario names, reference details, units, seeds and evidence cases from its accepted file. No row is implemented by the bootstrap.

| ID | Saved editable field | Inclusive whole-number range | Server result family |
| --- | --- | --- | --- |
| S01 materials | packCount | 1-20 | stored pack price x saved count |
| S02 films | screeningCount | 1-3 | stored runtime x saved count |
| S03 plants | plantCount | 1-30 | stored area x saved count |
| S04 activities | roundCount | 1-4 | stored minutes per round x saved count |
| S05 service tasks | taskUnits | 1-4 | stored labour minutes x saved units |
| S06 exhibits | allocatedMinutes | 5-60 | sum saved allocations; ignore suggested times |
| S07 print options | sheetCount | 1-200 | stored price x saved sheets |
| S08 games | roundCount | 1-5 | stored duration x saved count |
| S09 stations | stationCount | 1-10 | stored capacity x saved count |
| S10 extracts | minutesPerPage | 1-5 | stored pages x saved rate |
| S11 lamps | lampCount | 1-12 | stored watts x saved count |
| S12 article ideas | allocatedWords | 50-800 | sum saved allocations; ignore estimates |
| S13 drills | repetitionCount | 1-6 | stored minutes x saved count |
| S14 event tasks | workUnits | 1-10 | stored effort x saved units |
| S15 artworks | spacingCm | 0-50 | sum each stored width + saved allowance once |
| S16 demonstrations | preparationMinutes | 0-30 | sum each stored runtime + saved allowance once |
| S17 walking segments | traversalCount | 1-3 | stored metres x saved traversals |
| S18 equipment | unitCount | 1-15 | stored kg x saved units |
| S19 podcast segments | allocatedSeconds | 30-600 | sum saved allocations; ignore suggestions |
| S20 signs | copyCount | 1-25 | stored square centimetres x saved copies |

Do not impose a quantity/minimum-one/product-price model on allocations, rates or zero-valid allowances. Do not add catalogue suggestions to saved-allocation totals. Do not accept a client-supplied authoritative total. Use the assigned file's exact list/detail/create/get/POST/PUT/DELETE endpoints and code-field names.

## Evidence TODOs

Complete evidence/integration-evidence.md, testing-debugging-evidence.md and contribution-evidence.md with actual work. Follow the assigned four evidence cases, the brief's common success/error requirements, genuine debugging and source/AI-use records. Templates and the bootstrap seed are not evidence of completed assessment work.
