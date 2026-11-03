# Project objectives and progress

## Scope

Quatro Kantos selected Option 1: Feature Enhancements to the Lab 4.9.2 MapQuest application for DEVASC Project Activity 3. Official Agile roles come from Project Activity 2: Josh Ong — Scrum Leader; Dylan Garcia — Recorder; Miguel Yanto and Sean Suaco — Development Team.

Objectives:

1. Let users select miles or kilometers, preserving miles and converting to kilometers with miles × `1.60934`.
2. Improve readability with headings, labels, a trip summary, and organized directions.
3. Handle blank/invalid inputs and unsuccessful or invalid route responses with helpful messages.
4. Preserve live geocoding, routing, vehicle profiles, duration, and directions.
5. Use separate branches, testing, review, and pull requests to integrate the work.
6. Keep an evidence-based record of progress and tests without treating pending work as complete.

## Work ownership

| Member | Working branch | Scope |
| --- | --- | --- |
| Miguel Yanto | `distance-units` | Unit selection; no formatting/error-handling feature work |
| Sean Suaco | `formatting-errors` | Formatting and error handling; no unit selector |
| Dylan Garcia | `testing-documentation` | README, objectives, workflow, rubric and testing records; no application-code changes |
| Josh Ong | Team coordination | Scrum leadership and integration coordination |

Other repository branches are not substitutes for the member branches specified above. Dylan uses `testing-documentation`, not the existing `documentation` branch.

## GitHub workflow

1. Inspect `git status` and `git branch --show-current`. Work on the assigned branch, never directly on `main`.
2. Preserve existing changes before switching branches. Fetch remote updates; start new work from the agreed base version.
3. Make changes within the assigned scope. Keep separate features independent until integration.
4. Run relevant tests and record the actual inputs, results, date, version, and tester. Separate controlled responses from live API checks.
5. Review `git diff` and stage only intended files. Miguel's commit message is `Add distance unit selection`; Sean's is `Improve formatting and error handling`.
6. Commit and push to the assigned branch. Open or update a PR targeting `main`, describing the change, validation, and remaining limitations.
7. Review and resolve integration conflicts. Miguel and Sean edit overlapping application code, so neither feature should be overwritten during conflict resolution.
8. After both features are merged, Miguel and Sean help test the integrated application. Dylan records their reports and evidence. Josh coordinates review and completion.

For documentation, inspect `git diff --name-only` before staging. Stage README and documentation files explicitly; `mapquest.py` belongs to the developers' feature work.

## Progress snapshot

Recorded 4 November 2026 (Asia/Singapore). Update this snapshot when new evidence arrives.

| Work item | Evidence / observed state | Outstanding work |
| --- | --- | --- |
| Original app | `main` at `1d6a07a`; GraphHopper geocoding/routing and car/bike/foot profiles | Preserve functionality through integration |
| Miguel's enhancement | `distance-units` at `6610fff`; commit `Add distance unit selection`; [PR #1](https://github.com/joshong05/DEVASC-MapQuest-Enhancement/pull/1) open into `main` | Miguel's manual confirmation, review, merge, and integrated testing |
| Sean's enhancement | Local implementation verified by the assistant; saved in stash named `Sean formatting-errors work preserved before Dylan documentation`. Remote branch remains at `1d6a07a` | Restore draft on Sean's branch, obtain his test confirmation, commit, push, and create PR |
| Recorder documentation | README and documentation drafted on `testing-documentation` | Dylan review, developer reports, actual rubric, documentation commit and PR |
| Combined application | No combined-version test evidence recorded | Merge both features and run integration tests on the resulting commit |

## Evidence to preserve

- Project Activity 2 role assignment and the actual Activity 3 instructions/rubric.
- Each member's branch name and scoped diff.
- Miguel's and Sean's actual test inputs/results, labeled with branch, commit or draft state, and tester.
- Feature and documentation commit hashes and PR URLs; review and merge records when available.
- Final integrated application's commit and screenshots proving both enhancements work together.

Keep originals and identify their owner/date. Redact API keys before sharing screenshots. No screenshots or developer-authored test reports have been supplied for this record yet.
