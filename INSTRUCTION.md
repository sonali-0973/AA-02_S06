# AA-02: from group formation to submission

Follow these actions for your assigned S01–S20 scenario. Read the assessment brief, your scenario file, [README.md](README.md), [REQUIREMENTS.md](REQUIREMENTS.md), and the three templates in `evidence/` for detail. The starter is an unfinished runnable bootstrap. Its untouched checker results are **C01–C10 all FALSE**.

1. **Complete your group of three.** Confirm three members. Record each ID, name, and actual contribution in the manifest and contribution evidence. Agree how you will integrate and review work.

2. **Confirm one unique scenario through the fair allocation method.** Obtain the Course Leader's assigned S01–S20 ID and title. Confirm the Week 11 deadline date, time, and time zone with the Course Leader.

3. **Obtain and read the assigned scenario, brief and starter.** Copy the starter into your group workspace. Read your `aa-02-sXX.md` file and the assessment brief. Keep `submission-manifest.yml`, `README.md`, `frontend/`, `backend/`, `database/`, `config/`, `evidence/`, the checker, and these instructions.

4. **Prepare the tools and verify configuration.** Start the class-approved Docker engine and check Compose v2 with `include` support. Install host Python 3.10+ for the checker. From the project root run:

   ```sh
   docker version
   docker compose version
   docker compose -f config/docker-compose.yml config
   ```

   Resolve configuration and port issues. Document your actual verification result in the README Setup Instructions. You may retain working starter configuration; make only changes your implementation needs.

5. **Run and inspect the bootstrap.** Run `docker compose -f config/docker-compose.yml up --build -d --wait`, then `docker compose -f config/docker-compose.yml ps`. Open `http://127.0.0.1:8080` and inspect health, catalogue, and the unfinished collection control. The collection HTTP 501 response is expected here and is not a scenario success.

6. **Agree the scenario contract and shared interfaces.** Record your assigned endpoints, field names, seed values, validation bounds, calculation, success case, and error case. Use one mock session code for collection requests; this is not authentication. The assigned scenario file is authoritative.

7. **Implement the assigned workflow across all layers.** Replace the neutral frontend, API, and database bootstrap with your scenario's catalogue, saved collection, validation, ownership checks, and server-calculated result. Implement add, edit, remove, retrieval, and visible errors. Use [REQUIREMENTS.md](REQUIREMENTS.md) for adaptation points. Do not treat bootstrap connectivity as completion.

8. **Run the scenario evidence cases and investigate a real issue.** Test add, edit, remove, and invalid edit with the same mock session. Record actual requests, browser behaviour, database observations, expected and observed results, and unchanged state after rejection. Reproduce one genuine issue, fix it, and retest. Verify repeatable setup from your submitted files.

9. **Complete the required evidence and acknowledgements.** Fill every heading in [integration evidence](evidence/integration-evidence.md), [testing and debugging evidence](evidence/testing-debugging-evidence.md), and [contribution evidence](evidence/contribution-evidence.md) with substantive observations. Document each member's work, sources, and required AI tool use, incorporated outputs, and verification or changes. Include screenshots, exports, or logs only when referenced; link local assets relative to the evidence file. Never invent observations.

10. **Complete the manifest and project README.** Replace all identity and scenario placeholders in `submission-manifest.yml`. Keep its required artefact paths. Update every required README section with your actual project, routes, setup result, run commands, and known limitations. Make URLs and commands match the submitted configuration.

11. **Run the local structural checklist and resolve failures.** From the project root run:

   ```sh
   python -m pip install -r config/checker-requirements.txt
   python check_submission.py .
   ```

   Fix every FALSE and rerun. C01–C10 initially all report FALSE. TRUE is a local readiness heuristic, not proof of correct functionality, authentic evidence, or an assessment grade. Review the actual work yourself.

12. **Prepare a clean archive and check the archive itself.** Stage the required project files and all referenced evidence assets in a new folder. Exclude caches, existing ZIPs, real secrets, and machine-specific files. From inside the staged folder, replace `YourGroupID` with the manifest group ID and create the ZIP in its parent:

   ```powershell
   python -m zipfile -c ../128-353-AA2-YourGroupID.zip submission-manifest.yml README.md INSTRUCTION.md REQUIREMENTS.md check_submission.py frontend backend database config evidence .dockerignore .gitignore
   ```

   On macOS/Linux, use `python3` instead of `python`. Add any other root files your application needs. Inspect the ZIP and run `python check_submission.py ../128-353-AA2-YourGroupID.zip`; resolve C01–C10 and archive A01/A02 failures. The ZIP must contain the project at its root or in one enclosing folder.

13. **Upload to Canvas and confirm the deadline manually.** Upload the checked `128-353-AA2-GroupID.zip` to the AA-02 Canvas submission before the Course Leader's confirmed Week 11 deadline. Check the upload receipt/status and retain the archive and confirmation. The local checker cannot verify Canvas delivery or deadline compliance.
