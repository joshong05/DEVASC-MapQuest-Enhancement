# Quatro Kantos: MapQuest, Enhanced

DEVASC Project Activity 3 — **Option 1: improve the Lab 4.9.2 app.**

The app finds routes and shows distance, travel time, and directions. We chose it to improve an existing Python app and practice teamwork with GitHub.

Despite its MapQuest name, the supplied code uses **GraphHopper**. Confirm with the instructor that this lab version is accepted.

## Team

| Member | Role | Work |
| --- | --- | --- |
| Josh Ong | Scrum Leader | Guide the team and track progress |
| Dylan Garcia | Recorder | Keep documents and test records |
| Miguel Yanto | Development Team | Miles/kilometers choice |
| Sean Suaco | Development Team | Clear output and error messages |

## Features

- Choose miles or kilometers. Press Enter for miles.
- Convert using **miles × 1.60934** for totals and directions.
- Read a clear trip summary and numbered directions.
- Get helpful messages for empty input, wrong choices, and API errors.
- Use car, bike, or foot routes; plan more trips or quit.

All three PRs are merged into `main`. Eight automated test methods passed. Live car-route checks also passed. Team members still need to submit their own test results and screenshots.

## Setup

You need Python 3, Git, internet access, and a working GraphHopper key in `mapquest.py`. Keep keys out of screenshots and new commits. VS Code needs the Python extension.

In PowerShell:

```powershell
git clone https://github.com/joshong05/DEVASC-MapQuest-Enhancement.git
cd DEVASC-MapQuest-Enhancement
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
code .
```

Already have the project? Save your changes, switch to `main`, then run `git pull --ff-only`.

In VS Code, use **Python: Select Interpreter** and choose `.venv\Scripts\python.exe`.

## Use the app

```powershell
.\.venv\Scripts\python.exe mapquest.py
```

1. Enter `car`, `bike`, or `foot`.
2. Enter `m` for miles or `k` for kilometers. Enter alone selects miles.
3. Enter a start, such as `Manila, Philippines`.
4. Enter an end, such as `Quezon City, Philippines`.
5. Read the results, then try another trip.

Type `q` or `quit` at any prompt to exit. Blank locations ask again. Wrong choices or API failures return to the vehicle menu.

## Tests and fixes

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

These tests use sample API replies, not live requests. See the test record for live results.

- Python missing: install Python 3 and reopen the terminal.
- `requests` missing: run the install command above.
- API error: check your internet, key, and route choice.
- Location missing: check spelling or add a city/country.

## More information

- [Project plan and progress](docs/PROJECT.md)
- [Test results](docs/TESTING.md)
- [Required work](docs/RUBRIC.md)
- [Future ideas](docs/BACKLOG.md)
- [Presentation script](docs/PRESENTATION.md)
