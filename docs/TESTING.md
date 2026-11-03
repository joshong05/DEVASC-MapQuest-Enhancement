# Testing record

## Recording rules

Record actual observations, not assumed outcomes. A test plan is not a test result. A developer's feature branch passing does not establish that the integrated application passes.

The checks below were run by the **Codex assistant in the local workspace**, not personally reported by Miguel or Sean. They are transcribed from observed session output on 4 November 2026 (Asia/Singapore); screenshots and separate saved test logs have not been provided. The temporary test harnesses were not committed to the repository.

## Observed assistant verification

| ID | Version | Method and inputs | Actual observed result | Status / limitation |
| --- | --- | --- | --- | --- |
| A-M1 | Miguel `6610fff` | Controlled API responses: 16,100-meter total, 8,050-meter instruction, 900,000-ms duration; five unit inputs (`m`, `k`, blank, ` K `, `kilometers`) across car/bike/foot | All 15 scenarios passed. Total: 10.0 miles or 16.1 kilometers; instruction: 5.0 miles or 8.0 kilometers; duration 00:15:00. Multiplier, query parameters, and three-request flow checked. | Controlled data; not a live-provider claim |
| A-M2 | Miguel `6610fff` | Controlled route HTTP 400 with a JSON error message | Original error message displayed; scenario passed | One route-failure scenario; not exhaustive error handling |
| A-M3 | Miguel `6610fff` | Live car route: Manila, Philippines → Quezon City, Philippines; separate `m` and `k` selections | Each run returned HTTP 200 for both geocoding requests and routing. Totals: 8.0 miles / 12.9 kilometers; duration 00:20:30 in both runs. | Historical observation; live routes may change; Miguel confirmation pending |
| A-S1 | Sean local draft on `formatting-errors`, uncommitted and stashed | 27 controlled scenarios covering car/bike/foot, blank/invalid inputs, quitting, unknown locations, HTTP failures, invalid JSON/data, timeouts, connection failure, malformed routes/instructions, and retry after failure | All 27 passed. Valid fixture: 10.0 miles / 16.1 km, 00:15:00, numbered directions. Errors displayed without crashing in the tested scenarios. | Draft only; no final feature commit available |
| A-S2 | Same Sean draft | Live car route: Manila, Philippines → Quezon City, Philippines | Three HTTP 200 responses; trip summary and 13 numbered directions; 8.0 miles / 12.9 km; 00:20:30 | Assistant observation; Sean confirmation pending |
| A-S3 | Same Sean draft | Live starting location `zzzznonexistentlocation987654321zzzz` | HTTP 200 with no matching location; friendly “Location not found” message; application returned to the menu and exited on `q` | No real route request was expected or made |

Syntax and `git diff --check` passed for both implementations before these snapshots. The assistant checks do not replace member confirmation or final integration testing.

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

## Final integration plan

All cases below are **Not run**. Record the merged `main` commit before testing.

| ID | Test after both enhancements are merged | Evidence required | Status |
| --- | --- | --- | --- |
| I-01 | Valid route with miles selected | Unit selection, readable summary, numbered directions, duration, total and instruction units | Not run |
| I-02 | Same route with kilometers selected | Conversion using 1.60934 and consistent labels; same route/time subject to provider changes | Not run |
| I-03 | Blank/invalid inputs, unmatched location, and controlled API failure | Helpful messages; retry works and selected units remain correct on subsequent routes | Not run |
| I-04 | Car/bike/foot routes and quitting | Original profile selection and exit behavior still work | Not run |

Miguel and Sean help execute these tests; Dylan records their actual findings. Preserve failures and follow-up issues as well as passing evidence.
