# MapQuest, Enhanced — presentation script

Prepared for Quatro Kantos after code integration. This is a speaking script and demonstration plan, not evidence that the presentation has been delivered. Before presenting, confirm the latest main commit, run the demo, and update any observed numbers. Do not claim that the members personally performed assistant-run tests.

## Josh — introduction and choice

Good day. We are Team Quatro Kantos. For DEVASC Project Activity 3, we selected Option 1: feature enhancements to the Lab 4.9.2 application. We chose it because it gave us an existing Python/REST baseline for practical usability improvements and collaborative GitHub development.

Our project is called MapQuest, Enhanced. The supplied code in our repository uses GraphHopper for geocoding and routing. We retained that API foundation while adding distance-unit selection, clearer output, and friendlier handling of invalid input and route failures.

## Dylan — roles and process

We kept our Activity 2 roles: Josh Ong is Scrum Leader; I, Dylan Garcia, am Recorder; Miguel Yanto and Sean Suaco form the Development Team. Miguel's assigned feature was miles/kilometers selection. Sean's was formatting and error handling. My records cover objectives, workflow, testing evidence, and future work.

We used separate branches and pull requests. Miguel's PR #1 and Sean's PR #3 were merged into main. Both features touched the same file, so integration preserved the unit selector while keeping the improved summary, numbered directions, and error handling. Documentation was prepared in PR #2. Show the actual repository and merge history here. Do not imply that a human review approval was recorded unless the team has that evidence.

## Miguel — distance units

The original version displayed both miles and kilometers. Our enhancement lets users choose one unit for totals and turn-by-turn distances. Miles retain the original calculation; selecting kilometers applies miles times 1.60934. Blank unit input defaults to miles. Invalid choices receive a helpful message.

## Sean — readability and errors

The integrated app uses a clear trip summary with starting location, destination, vehicle, distance, and duration. Directions are numbered. Blank fields prompt again. Invalid vehicle or unit choices, unknown locations, connection failures, timeouts, and invalid API responses produce helpful feedback. Users can retry or quit without replacing the live routing with fixed sample results.

## Miguel — verification, with accurate attribution

The assistant ran eight repeatable unittest methods with controlled responses, including all three requested vehicle profiles, the exact conversion factor, invalid data, quitting, and recovery after an error. Those tests passed on the merged code. Separate live integrated checks for Manila to Quezon City returned 8.0 miles or 12.9 kilometers with a duration of 00:20:30. A nonexistent location produced a friendly error. These are recorded observations; live results can change.

At the time this script was prepared, our personal test confirmations and screenshots had not yet been added. After we perform those tests, we will update the record with our actual results rather than assume them.

## Sean — demonstration

Use the current main version and show its commit before the demo.

1. Start the app. Enter `car`, then `m`, then `Manila, Philippines` and `Quezon City, Philippines`. Explain the summary and numbered directions using the actual output.
2. Repeat with `car` and `k` for the same locations. Point out the selected unit in the total and instructions. Do not calculate from rounded display values to claim an exact conversion.
3. At the next vehicle prompt, enter `plane` to show validation. Try a blank profile/location or a clearly nonexistent location to show the appropriate feedback.
4. Enter `q` and show the clean exit.

If the API is unavailable, explain the failure honestly; use clearly labeled controlled test evidence rather than presenting a fixture as a successful live route.

## Dylan — future work and evidence

Our proposed Activity 4 backlog includes safer API configuration, automated PR checks, saved routes, a GUI, an interactive map, and investigation of traffic-aware routing. These items are future proposals, subject to team approval and provider support.

Our records distinguish implementation, assistant verification, and member confirmations. We will preserve branch and merge history, real inputs/results, screenshots, and the presentation evidence. Member skillsets, availability, and schedule information must be supplied by the team before claiming those records are complete.

## Josh — conclusion

We have integrated distance-unit selection, clearer output, and error handling while preserving the application's live routing purpose. The recorded automated and live checks passed for the scenarios tested. Our remaining handoff work is to confirm the team evidence, rehearse the demonstration, and complete the instructor's submission requirements. Thank you.
