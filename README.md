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
- Convert using **1 mile = 1609.344 meters** for totals and directions.
- Read a clear trip summary and numbered directions.
- Get helpful messages for empty input, wrong choices, and API errors.
- Use car, bike, or foot routes; plan more trips or quit.
- Review up to five geocoding matches with coordinates, then choose and confirm each location.
- Use either the terminal app or the desktop GUI with an interactive map:
  - Route drawn on the map with start/end pins; click any direction step to highlight and zoom to it.
  - Location matches appear as numbered pins, so you can pick the right one visually.
  - Right-click the map to set a start or destination at that point.
  - Map styles: Streets, Light, Dark, Satellite, Terrain; light/dark app theme.
  - Distance, duration, and arrival-time summary; copy directions to the clipboard.

The original team's PRs are merged into `main`. The current improvements add location confirmation and a GUI. Run the tests below for the current result; earlier live checks do not verify these new changes.

## Setup

You need Python 3, internet access, and a GraphHopper API key. The key previously stored in `mapquest.py` was exposed; rotate it in your GraphHopper account before using this version. Do not commit or screenshot the replacement key. VS Code needs the Python extension.

In PowerShell:

```powershell
git clone https://github.com/joshong05/DEVASC-MapQuest-Enhancement.git
cd DEVASC-MapQuest-Enhancement
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env   # then open .env and paste your key
code .
```

### Getting the API key

1. Create a free account at [graphhopper.com](https://www.graphhopper.com/) and open the dashboard.
2. Go to **API Keys** and create a key.
3. Put it in the `.env` file in the project folder: `GRAPHHOPPER_API_KEY=your-key`.

`.env` is git-ignored, so the key is not committed. You can instead set it per terminal session with `$env:GRAPHHOPPER_API_KEY = "your-key"`; the environment variable takes priority over `.env`.

If GraphHopper cannot be reached, the app switches to free OpenStreetMap services (Nominatim for place search, OSRM for routes). To force one provider, add `ROUTING_PROVIDER=graphhopper` or `ROUTING_PROVIDER=osm` to `.env`.

In VS Code, use **Python: Select Interpreter** and choose `.venv\Scripts\python.exe`.

## Use the app

```powershell
.\.venv\Scripts\python.exe mapquest.py
# Or open the desktop GUI:
.\.venv\Scripts\python.exe mapquest_gui.py
```

1. Enter `car`, `bike`, or `foot`.
2. Enter `m` for miles or `k` for kilometers. Enter alone selects miles.
3. Search for a start, such as `Manila, Philippines`. Select a numbered match and confirm it, or enter `r` to search again.
4. Do the same for the destination, such as `Quezon City, Philippines`.
5. Read the results, then try another trip. In the GUI, type a place and press Enter, click the right match (in the list or on the map), then click **Find route** (Ctrl+Enter).

In the terminal, type `q` or `quit` at any prompt to exit. Blank locations ask again. Failed location searches can be retried; a failed route returns to the vehicle menu. In the GUI, requests run in a background thread so the window remains responsive.

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
