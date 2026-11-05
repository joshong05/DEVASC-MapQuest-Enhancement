# Test results

**Tester: Codex assistant.** These checks do not count as Miguel's or Sean's personal reports.

## Location confirmation, GUI, and OpenStreetMap fallback

**Tester: Claude Code assistant, run on Sean's machine.** Date: 5 November 2026. Code: uncommitted working tree based on `59afb13`, committed on branch `gui-location-confirm`. Setup: Windows 11, Python 3.11.9.

| Check | Actual result |
| --- | --- |
| Automated tests (`unittest discover`) | 22 tests, all passed (sample replies, no live requests) |
| Live terminal trip: Manila → Quezon City, car, kilometers | 12.9 kilometers; 00:18:00; 20 numbered directions |
| Wrong vehicle (`plane`), wrong unit (`x`), blank location | Clear message each time; asked again |
| Made-up location | "Location not found" message; asked again |
| Match number out of range (`9`), then select and confirm | Asked again; selection and `y` confirmation worked |
| `q` at the vehicle prompt | Printed "Goodbye!" and exited |
| GUI launch (`mapquest_gui.py`) | Window opened; closed with exit code 0 and no errors logged |
| GraphHopper reachability | **Blocked:** `graphhopper.com` timed out from this network, so the app used the OpenStreetMap fallback (Nominatim + OSRM) for every live result above |

Still needed:

- Repeat the live trip with `ROUTING_PROVIDER=graphhopper` on a network that can reach GraphHopper, to confirm the API key works.
- Test the GUI by hand: search, pick a match from the list and from the map, right-click to set a point, route drawing, clicking a direction step, map styles, and copying directions. The GUI has no automated tests.

## Combined app

Date: 4 November 2026, Asia/Singapore. Code: `4c7c3b1` on `main`. Setup: Windows, Python 3.14.10.

[Full saved output](evidence/integration-checks.txt)

| Check | Actual result |
| --- | --- |
| Eight automated test methods | All passed, including their sample cases |
| Miles, kilometers, and blank unit choice | Correct totals and directions for car/bike/foot sample replies |
| Exact conversion check | 1,000 miles became 1609.3 km; a 500-mile step became 804.7 km |
| Blank/wrong input, bad API replies, timeout, retry, and quit | Helpful errors; tested cases did not crash |
| Live car route: Manila → Quezon City, miles | HTTP 200; 8.0 miles; 00:20:30; numbered directions |
| Same live route, kilometers | HTTP 200; 12.9 kilometers; 00:20:30 |
| Live made-up location | Helpful location-not-found message; returned to menu |

Live route values can change. Sample replies do not prove every real bike/foot route works. Use the unrounded miles value when checking conversion.

Run the automated tests:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Earlier checks

Before combining the features:

- Miguel's `6610fff`: 15 unit/profile cases and one route-error case passed. Live car runs showed 8.0 miles or 12.9 kilometers, both 00:20:30.
- Sean's draft: 27 sample cases passed. A live route showed 8.0 miles / 12.9 km, 00:20:30, and 13 directions. A made-up location showed a clear error.
- Both passed syntax and Git whitespace checks.

Those early checks used temporary test scripts. The combined app's tests are saved in `tests/test_mapquest.py`.

## Tests still needed from members

| Tester | What to try | Status |
| --- | --- | --- |
| Miguel | Same route in miles and kilometers; blank unit choice | No personal report yet |
| Sean | Valid car/bike/foot routes, blank input, wrong choices, missing location, quit | No personal report yet |
| Sean | API failure or bad reply using a clearly labeled sample test | No personal report yet |

Save screenshots and failures too. Use this short record for each test:

```text
Tester and date/time:
Branch and commit:
Python version / OS:
Live API or sample reply:
Inputs:
Expected result:
Actual result:
Pass / Fail / Blocked:
Screenshot or log:
Follow-up:
```
