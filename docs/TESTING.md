# Testing record

## Recording rules

Record actual observations, not assumed outcomes. A test plan is not a test result. A developer's feature branch passing does not establish that the integrated application passes.

The checks below were run by the **Codex assistant in the local workspace**, not personally reported by Miguel or Sean. They are transcribed from observed session output on 4 November 2026 (Asia/Singapore); screenshots and separate saved test logs have not been provided. The early feature-only checks used temporary harnesses. The integrated version now includes repeatable tests in tests/test_mapquest.py and a saved integration report linked below.

## Observed assistant verification

| ID | Version | Method and inputs | Actual observed result | Status / limitation |
| --- | --- | --- | --- | --- |
| A-M1 | Miguel `6610fff` | Controlled API responses: 16,100-meter total, 8,050-meter instruction, 900,000-ms duration; five unit inputs (`m`, `k`, blank, ` K `, `kilometers`) across car/bike/foot | All 15 scenarios passed. Total: 10.0 miles or 16.1 kilometers; instruction: 5.0 miles or 8.0 kilometers; duration 00:15:00. Multiplier, query parameters, and three-request flow checked. | Controlled data; not a live-provider claim |
| A-M2 | Miguel `6610fff` | Controlled route HTTP 400 with a JSON error message | Original error message displayed; scenario passed | One route-failure scenario; not exhaustive error handling |
| A-M3 | Miguel `6610fff` | Live car route: Manila, Philippines → Quezon City, Philippines; separate `m` and `k` selections | Each run returned HTTP 200 for both geocoding requests and routing. Totals: 8.0 miles / 12.9 kilometers; duration 00:20:30 in both runs. | Historical observation; live routes may change; Miguel confirmation pending |
| A-S1 | Sean local draft on `formatting-errors`, uncommitted and stashed | 27 controlled scenarios covering car/bike/foot, blank/invalid inputs, quitting, unknown locations, HTTP failures, invalid JSON/data, timeouts, connection failure, malformed routes/instructions, and retry after failure | All 27 passed. Valid fixture: 10.0 miles / 16.1 km, 00:15:00, numbered directions. Errors displayed without crashing in the tested scenarios. | Historical draft check; later committed as 56db283 and integrated through PR #3 |
| A-S2 | Same Sean draft | Live car route: Manila, Philippines → Quezon City, Philippines | Three HTTP 200 responses; trip summary and 13 numbered directions; 8.0 miles / 12.9 km; 00:20:30 | Assistant observation; Sean confirmation pending |
| A-S3 | Same Sean draft | Live starting location `zzzznonexistentlocation987654321zzzz` | HTTP 200 with no matching location; friendly “Location not found” message; application returned to the menu and exited on `q` | No real route request was expected or made |

Syntax and `git diff --check` passed for both implementations before these snapshots. The feature-only checks do not replace member confirmation; integrated verification is recorded below.

## Developer reports awaiting submission

| Tester | Requested evidence | Current state |
| --- | --- | --- |
| Miguel Yanto | Miles/kilometers runs, selected unit, actual totals and directions, route/profile, tested commit, screenshots | Not yet supplied |
| Sean Suaco | Valid route, blank/invalid inputs, unmatched location, quitting, tested draft/commit, screenshots | Not yet supplied |

Copy this template for each developer test after the tester provides results:

```text
Test ID:
Tester:
Date/time and timezone:
Branch and commit (or explicitly identified uncommitted draft):
Environment (Python version / OS):
Method (live API / controlled response / manual input):
Inputs, including vehicle, locations, and unit if applicable:
Expected result:
Actual result (quote output or attach evidence):
Result (Pass / Fail / Blocked / Not run):
Screenshot or log filename/link:
Issue or follow-up:
```

## Manual test plan

These are planned cases. Their rows remain **Not run by developer** until Miguel or Sean supplies their actual results.

| ID | Owner | Inputs / action | Expected behavior | Developer result |
| --- | --- | --- | --- | --- |
| M-01 | Miguel | Same route with `m`, then `k` | Miles retained; kilometers use miles × 1.60934 before display rounding; totals and instructions show selected unit | Not run by developer |
| M-02 | Miguel | Same route with a blank unit choice | Miles selected by default | Not run by developer |
| S-01 | Sean | Valid car route, then valid bike/foot routes where supported by the API | Readable summary, labels, numbered directions, and valid duration/distance | Not run by developer |
| S-02 | Sean | Blank/whitespace input at each prompt; invalid profile such as `plane` | Helpful validation; no inappropriate API request or crash | Not run by developer |
| S-03 | Sean | Unmatched location | Friendly location error; no route calculated from invalid coordinates | Not run by developer |
| S-04 | Sean | `q` / `quit` at each input prompt | Clean exit | Not run by developer |
| S-05 | Sean | Controlled timeout, HTTP error, malformed/empty route response | Friendly message and ability to try again | Not run by developer |

For M-01, use the unrounded underlying miles when checking conversion. Multiplying a displayed one-decimal miles value can differ from the displayed kilometers because of rounding. Report controlled fixtures separately from real API output.

## Integrated verification

The integrated application was merged into main at **4c7c3b1** through [PR #1](https://github.com/joshong05/DEVASC-MapQuest-Enhancement/pull/1) and [PR #3](https://github.com/joshong05/DEVASC-MapQuest-Enhancement/pull/3). Sean's initial feature commit is **56db283** (`Improve formatting and error handling`); the merge-resolution commit is **d94a9f4**. Tests were committed in **69c65d8**.

Tester: Codex assistant. Date: 4 November 2026, Asia/Singapore. Environment: Windows, Python 3.14.10, project virtual environment. See the [saved integration report](evidence/integration-checks.txt) for commands, code identity, and actual output. Personal member confirmations remain pending.

| ID | Integrated test | Observed result | Status |
| --- | --- | --- | --- |
| I-01 | Controlled fixtures for miles/default and kilometers across car/bike/foot | Selected-unit totals and numbered instructions correct; duration 00:15:00; API query coordinates/profile preserved | Pass, controlled responses |
| I-02 | Exact conversion fixture: 1,000 base miles, 500-mile instruction | 1609.3 kilometers total and 804.7 kilometers instruction after display rounding; distinguishes 1.60934 from 1.61 | Pass, controlled responses |
| I-03 | Blank/invalid choices, unknown location, timeout/HTTP/malformed-data cases, retry and unit change | Helpful messages, no invalid route calculation, clean quitting and successful retry in tested cases | Pass, controlled responses |
| I-04 | Live Manila → Quezon City, car, miles | Both geocoding requests and route HTTP 200; 8.0 miles; 00:20:30; numbered directions | Pass, live observation |
| I-05 | Same live route, kilometers | Three HTTP 200 responses; 12.9 kilometers; 00:20:30; numbered directions in kilometers | Pass, live observation |
| I-06 | Live nonexistent location | HTTP 200 with no match; friendly location-not-found message and return to menu | Pass, live observation |

Run the repeatable suite from the repository folder:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Eight test methods with subcases passed on the merged code. The controlled tests do not prove provider support for every vehicle/location combination; live checks here used car. API data and account availability can change. No personal developer test or independent human review is inferred from assistant checks.

## Remaining team verification

Miguel and Sean should run the current main application, confirm their own actual results using the template above, and preserve screenshots. Dylan should add those reports with the tested commit and date. Capture the merged branch/PR history and rehearse the presentation using actual output. Retain any failures and follow-up issues.
