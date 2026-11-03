# Quatro Kantos: MapQuest Enhancements

DEVASC Project Activity 3 — **Option 1: Feature Enhancements** to the Lab 4.9.2 application.

The application finds a route between two locations and displays distance, duration, and numbered directions. The project retains the lab's MapQuest name, but this repository's supplied code uses **GraphHopper** for geocoding and routing. Confirm with the instructor that this supplied lab version is acceptable.

## Team

| Member | Official Agile role | Assigned work |
| --- | --- | --- |
| Josh Ong | Scrum Leader | Coordination, progress monitoring, and integration coordination |
| Dylan Garcia | Recorder | Documentation, deliverable tracking, and progress/test records |
| Miguel Yanto | Development Team | Miles/kilometers selection |
| Sean Suaco | Development Team | Formatting and error handling |

We chose Option 1 to build on an existing Python/REST application, make practical improvements to everyday route output, and practice collaborative GitHub development with a manageable feature scope.

## Implemented on main

- Select miles or kilometers; blank unit input defaults to miles.
- Preserve the original miles calculation; convert miles to kilometers using **miles × 1.60934**. Both totals and directions display the selected unit.
- Clear trip summary, location/vehicle labels, and numbered directions.
- Validate blank inputs, unknown vehicle profiles, and invalid unit choices.
- Friendly messages for unknown locations, connection failures, timeouts, unsuccessful requests, and invalid route data.
- Preserve live geocoding/routing, car/bike/foot selection, duration, and repeated trips.

[PR #1](https://github.com/joshong05/DEVASC-MapQuest-Enhancement/pull/1) and [PR #3](https://github.com/joshong05/DEVASC-MapQuest-Enhancement/pull/3) were merged. Integrated code at `4c7c3b1` passed assistant-run tests. Member-authored confirmations and screenshots remain pending; see [testing](docs/TESTING.md).

## Requirements and installation

You need Python 3 with pip/venv, Git, internet access, and a valid GraphHopper API key in the `key` variable of `mapquest.py`. VS Code with its Microsoft Python extension is optional.

The source currently contains a key from the original application. If it stops working, configure your own key locally. Do not commit replacement credentials or show keys in screenshots.

In Windows PowerShell:

```powershell
git clone https://github.com/joshong05/DEVASC-MapQuest-Enhancement.git
cd DEVASC-MapQuest-Enhancement
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
code .
```

For an existing checkout, preserve current changes, switch to `main`, and run `git pull --ff-only` instead of cloning again. In VS Code, use **Python: Select Interpreter** and select `.venv\Scripts\python.exe`.

## Run and use

```powershell
.\.venv\Scripts\python.exe mapquest.py
```

1. Enter `car`, `bike`, or `foot`.
2. Choose `m` / `miles` or `k` / `kilometers`. Press Enter for miles.
3. Enter a starting location, such as `Manila, Philippines`.
4. Enter a destination, such as `Quezon City, Philippines`.
5. Read the summary and numbered directions, then plan another trip.
6. Type `q` or `quit` at any prompt to exit.

Inputs accept surrounding whitespace; vehicle and unit choices accept uppercase. Blank location/profile inputs prompt again. Invalid profile/unit choices and API failures return to the vehicle menu. Route values vary with provider data and profile availability.

## Run repeatable tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The eight test methods use controlled API responses and make no live HTTP calls. They cover conversion, all three requested profiles, formatting, invalid input, quitting, API/data failures, and retry behavior. Live observations and their limits are recorded separately.

## Troubleshooting

- Python not found: install Python 3 and reopen the terminal.
- Missing `requests`: run the requirements installation command with the same interpreter.
- HTTP error: check connectivity, key validity, and whether the provider supports the requested route/profile.
- Location not found: add a city/country or check spelling.
- Invalid route response: retry or choose another route/profile.

## Project records

- [Objectives, workflow, task priorities, and progress](docs/PROJECT.md)
- [Test results and member-report template](docs/TESTING.md)
- [Instruction/deliverable mapping](docs/RUBRIC.md)
- [Proposed Activity 4 backlog](docs/BACKLOG.md)
- [Presentation speaking script and demo plan](docs/PRESENTATION.md)

Preserve branch/commit, test, PR/merge, and presentation evidence. Hide credentials and identify the tester and tested version. Prior member experience, actual time commitments, collaborator-access evidence, and member confirmations must be supplied by the team rather than inferred.
