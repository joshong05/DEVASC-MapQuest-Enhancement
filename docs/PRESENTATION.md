# MapQuest, Enhanced — presentation script

Use the latest `main` for the demo. This script does not prove the presentation was delivered. Add personal test results only after the members provide them.

## Josh — introduction

Good day. We are Team Quatro Kantos. We chose Option 1: improve the Lab 4.9.2 app. It let us build on existing Python code and practice working together on GitHub.

Our project is MapQuest, Enhanced. The supplied code uses GraphHopper to find locations and routes. We added a unit choice, clearer output, and helpful error messages.

## Dylan — roles and workflow

We kept our Activity 2 roles. Josh is Scrum Leader. I am Dylan, the Recorder. Miguel and Sean are the Development Team.

Miguel worked on units. Sean worked on formatting and errors. I kept the project and test records.

We used separate branches and pull requests. PR #1 added units, PR #3 added formatting and errors, and PR #2 added documents. All three are merged into main. We fixed the code conflict while keeping both features.

[Show the real repository and merge history.]

## Miguel — units

The original app showed both miles and kilometers. Now users can choose one unit for the total and each direction. Kilometers use miles times 1.60934. Pressing Enter selects miles.

## Sean — output and errors

The app now shows a clear trip summary and numbered directions. Blank input asks again. Wrong choices, missing locations, and API failures show helpful messages. Users can try again or quit.

## Miguel — tests

The assistant ran eight automated test methods, and all passed. Live car-route checks from Manila to Quezon City showed 8.0 miles or 12.9 kilometers, both taking 00:20:30. A made-up location showed a clear error.

Live results may change. Our own test reports and screenshots still need to be added.

## Sean — demo

1. Show the current commit. Run the app.
2. Enter `car`, `m`, `Manila, Philippines`, then `Quezon City, Philippines`.
3. Explain the trip summary and directions using the actual output.
4. Repeat with `k` to show kilometers.
5. Enter `plane` or a blank field to show validation. Try a made-up location for an error.
6. Enter `q` to quit.

If the live API fails, explain it. Label any sample test output clearly.

## Dylan — future work

Our future ideas include safer key storage, automatic tests, saved routes, a graphical interface, maps, and traffic information. These are proposals for Activity 4, not finished features.

We will save real test results, screenshots, and project records for submission.

## Josh — closing

Both features are now on main, and the recorded tests passed. We still need the team's personal test evidence and presentation rehearsal. Thank you.
