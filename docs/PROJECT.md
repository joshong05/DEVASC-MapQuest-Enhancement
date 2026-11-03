# Project objectives, workflow, and progress

## Choice and objectives

Quatro Kantos selected Option 1: enhance the Lab 4.9.2 application. It provides an existing Python/REST baseline on which the team can demonstrate practical user-facing improvements, scoped work, and collaborative version control.

Objectives: selectable miles/kilometers with the specified 1.60934 multiplier; readable trip summaries and directions; friendly input/API error handling; preservation of live routing and vehicle profiles; GitHub branch/PR integration; documented verification and future improvements.

The supplied baseline uses GraphHopper despite the MapQuest lab/project name. The instructor's acceptance of that baseline is still to be confirmed.

## Roles, assignments, and skills

Official roles remain those established in Activity 2.

| Member | Role | Assigned contribution / relevant area | Prior experience |
| --- | --- | --- | --- |
| Josh Ong | Scrum Leader | Coordination, task priorities, GitHub workflow, integration | Awaiting Josh's description |
| Dylan Garcia | Recorder | Documentation, rubric mapping, progress/evidence records | Awaiting Dylan's description |
| Miguel Yanto | Development Team | Python input and distance conversion | Awaiting Miguel's description |
| Sean Suaco | Development Team | Python formatting, validation, API response handling | Awaiting Sean's description |

Assignments describe work scope, not verified expertise. The team should add actual skillsets and any cross-training completed. No prior experience or training outcome is inferred.

## Strategy and tools

Use small, separately owned tasks; implement the features independently; preserve baseline behavior; test each feature and their combination; record real evidence; integrate through PRs. Python, requests, Git/GitHub, VS Code, and unittest are the implementation and verification tools. Markdown files hold the shared project records.

Assigned branches: `distance-units` (Miguel), `formatting-errors` (Sean), `testing-documentation` (Dylan), and `project-management` (coordination work). `main` is the integrated version. Preserve current changes before switching branches; stage only intended files and never force-push or discard another member's work.

Actual integration used PR #1 for distance selection, PR #3 for formatting/error handling and conflict resolution, and PR #2 for documentation. Both developers changed mapquest.py; the conflict was resolved explicitly to retain both features. Automated and live checks were performed by the assistant. No independent human code-review approval is claimed.

## Task plan and dependencies

This is a prioritized completion/handoff plan, not a record of a previously agreed sprint schedule.

| Priority | Owner | Task | Dependency / completion evidence |
| --- | --- | --- | --- |
| P1 | Miguel | Implement unit selection and preserve baseline routing | Completed in 6610fff / PR #1 |
| P1 | Sean | Implement formatting and friendly error handling | Completed initial commit 56db283; integrated in PR #3 |
| P1 | Integration, coordinated by Josh | Resolve overlap; verify combined behavior | Integrated code 4c7c3b1; assistant tests and live checks recorded |
| P1 | Miguel and Sean | Personally run/confirm test cases; preserve screenshots | Pending member reports; integrated code available |
| P1 | Dylan | Update README, instructions mapping, test records, backlog, presentation script | Documentation PR #2 |
| P1 | Josh | Confirm instructor accepts the supplied GraphHopper baseline; verify collaborator access | Pending team evidence |
| P2 | All, coordinated by Josh | Review records, rehearse demonstration, capture presentation/submission evidence | Depends on member confirmations and instructor requirements |
| P2 | Dylan | Record real skills, availability, workload, and completion dates | Team-supplied information required |

Instructor deadline, allocated sprint count, budget, per-member availability, task estimates, and agreed check-in times have not been supplied. Josh should record those values and use them to assign dates and rebalance workload. Until then, no claim of finishing on schedule or within budget is made. Report blockers in the task record and prioritize dependencies before presentation rehearsal.

## Progress snapshot

4 November 2026, Asia/Singapore:

- Original baseline: 1d6a07a.
- Miguel's feature: committed/pushed and merged through PR #1.
- Sean's feature: restored from the saved draft, committed as `Improve formatting and error handling`, integrated with Miguel's work, and merged through PR #3.
- Integrated code: main commit 4c7c3b1; eight repeatable test methods passed on that commit. Live integrated checks are recorded separately in TESTING.md.
- Documentation: README, workflow, test record, instruction mapping, future backlog, and presentation script prepared through PR #2.
- Pending human evidence: Miguel/Sean personal test confirmations, member skillsets and availability, collaborator-access evidence, independent review, presentation rehearsal/delivery, and instructor baseline confirmation.

The earlier stash is retained as a backup of Sean's initial draft; it is no longer the only copy of his implementation.

## Evidence checklist

Preserve Activity 2 role assignments; actual member skill/availability notes; collaborator access; branch/commit diffs; test inputs/results; PRs and merges; integrated-version screenshots; and the final presentation/rehearsal evidence. Record failures as well as successes, and hide credentials.
