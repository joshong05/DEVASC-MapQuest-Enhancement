# Proposed future backlog — Project Activity 4

These are proposed future revisions, not implemented features or an approved sprint commitment. Priority is an initial suggestion for team/product-owner review; no cost or schedule estimate has been agreed.

| ID | Suggested priority | Proposed item and benefit | Acceptance idea | Dependency / investigation |
| --- | --- | --- | --- | --- |
| B-01 | High | Move API configuration to environment variables | Missing key gives clear setup instructions; no key committed or printed | Agree on credential/configuration approach |
| B-02 | High | Strengthen test automation and CI | PR checks run controlled tests before merge; optional live checks remain separate | GitHub Actions permissions and team review |
| B-03 | Medium | Save route summaries | User explicitly saves/reopens a route with locations, profile, units, and timestamp | Select a simple local file format |
| B-04 | Medium | Graphical user interface | Locations, profile, and unit inputs produce the same validated results as the CLI | Choose UI toolkit and preserve shared routing logic |
| B-05 | Medium | Interactive route map | Successful route can be displayed with start/end and path | Investigate route geometry, map library, provider terms |
| B-06 | Low | Live traffic or traffic-aware routing | Display traffic data only when a supported provider supplies it; explain unavailability | Confirm API support, cost, credentials, and instructor scope |

Unimplemented ideas must be described as future work in the presentation. Check provider capability rather than assuming the current GraphHopper account supplies traffic information. Bring these items to Activity 4 planning for approval, sizing, and assignment.
