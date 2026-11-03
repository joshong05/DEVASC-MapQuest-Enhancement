# Quatro Kantos: MapQuest Enhancements

DEVASC Project Activity 3 — **Option 1: Feature Enhancements** to the Lab 4.9.2 MapQuest Python application.

The application finds a route between two locations and displays distance, travel time, and driving/walking/cycling instructions. Although the lab/project name is MapQuest, the original code in this repository uses the **GraphHopper API** for geocoding and routing.

## Team

| Member | Official Agile role | Project responsibility |
| --- | --- | --- |
| Josh Ong | Scrum Leader | Coordinate work, review integration, and track team progress |
| Dylan Garcia | Recorder | Maintain documentation, rubric tracking, and progress/test records |
| Miguel Yanto | Development Team | Miles/kilometers selection and development testing |
| Sean Suaco | Development Team | Formatting, error handling, and development testing |

## Feature status

Documentation snapshot: **4 November 2026, Asia/Singapore**. A feature branch implementation is not the same as a merged feature.

| Version / branch | Behavior and status |
| --- | --- |
| `main` and this documentation branch | Original application: car/bike/foot profiles; route distance shown in both miles and kilometers; duration and directions. |
| `distance-units` | Unit selection implemented and pushed in `6610fff`. [PR #1](https://github.com/joshong05/DEVASC-MapQuest-Enhancement/pull/1) is open into `main`; Miguel's personal test confirmation is pending. |
| `formatting-errors` | Formatting and error-handling implementation exists locally, preserved in a Git stash. It is not committed or pushed; Sean's personal test confirmation and PR are pending. |
| Final integrated application | Both enhancements together have not been verified. Integration testing is pending after merge. |

The original application on `main` does **not** yet include either enhancement. See [project progress](docs/PROJECT.md) and [testing records](docs/TESTING.md) for the evidence and remaining work.

## Requirements and setup

- Python 3 with `pip` and `venv`.
- Git; VS Code with the Microsoft Python extension is recommended for editing.
- Internet access and a valid GraphHopper API key configured in the `key` variable in `mapquest.py`.

The repository currently contains a key in the source. Its continued validity is not guaranteed. If it no longer works, obtain your own GraphHopper key and configure it locally before live testing. Do not publish replacement keys in commits or screenshots.

In a Windows PowerShell terminal:

```powershell
git clone https://github.com/joshong05/DEVASC-MapQuest-Enhancement.git
cd DEVASC-MapQuest-Enhancement
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install requests
code .
```

If you already have a checkout, open its folder instead of cloning again. Verify your branch with `git branch --show-current` before making changes. Save or commit your current work on its own branch before switching; do not discard another member's changes.

In VS Code, use **Python: Select Interpreter** from the Command Palette and choose `.venv\Scripts\python.exe`. The commands below run that interpreter directly, so activating the environment is optional.

## Run the application

From the repository folder:

```powershell
.\.venv\Scripts\python.exe mapquest.py
```

For the original application on `main` or `testing-documentation`:

1. Choose a vehicle profile: `car`, `bike`, or `foot`.
2. Enter a starting location, for example `Manila, Philippines`.
3. Enter a destination, for example `Quezon City, Philippines`.
4. Read the total distance, trip duration, and turn-by-turn directions. Distances are displayed in both miles and kilometers.
5. Enter another route when prompted, or type lowercase `q` or `quit` at the vehicle, starting-location, or destination prompt to exit.

Route values depend on the locations, selected profile, and current API data. Example locations do not imply a fixed distance or duration.

### Testing an enhancement branch

Check out the relevant branch only after preserving any current work. Miguel's `distance-units` version adds a unit prompt **after the vehicle prompt**: enter `m` for miles, `k` for kilometers, or press Enter for miles. Kilometers are calculated as miles × `1.60934`; totals and directions use the selected unit.

Sean's local draft adds a trip summary, numbered directions, blank-input checks, and friendly API-error messages. The remote `formatting-errors` branch still has the original application at this snapshot, so switching to that remote branch alone will not retrieve his uncommitted draft. Recorder documentation does not restore or publish that application code.

## If something goes wrong

- If Python is not found, install Python 3 and reopen your terminal.
- If `requests` is missing, run the installation command above using the same environment as the app.
- If the API rejects a request, check connectivity and key validity. Retry with clear city/country names and an available vehicle profile.
- The original application has limited handling for blank inputs, unmatched locations, and malformed responses. Sean's handling of these cases remains a separate, unmerged enhancement.

## Project records

- [Objectives, development workflow, and progress](docs/PROJECT.md)
- [Observed verification, developer test template, and integration checklist](docs/TESTING.md)
- [Rubric and evidence tracker](docs/RUBRIC.md)

Preserve screenshots of branch names, relevant code changes, actual test inputs/results, commits, PRs, and final integration. Hide API keys in any captured terminal output or URLs. Tests must identify who performed them and which version was tested.
