"""Mocked API checks for the shared routing code and location selection."""

import contextlib
import io
import os
import tempfile
import unittest
from unittest.mock import Mock, patch

import requests
from urllib.parse import parse_qs, urlparse

import mapquest
import routing_service
from routing_service import (Location, RoutingError, format_distance, format_duration, format_trip, get_route,
                             get_route_details, search_locations)


def reply(data, status=200):
    return Mock(status_code=status, json=Mock(return_value=data))


class RoutingServiceTests(unittest.TestCase):
    def setUp(self):
        self.key = patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": "test-key", "ROUTING_PROVIDER": "graphhopper"})
        self.key.start()
        self.addCleanup(self.key.stop)

    def test_multiple_matches_include_names_and_coordinates(self):
        data = {"hits": [
            {"name": "Springfield", "state": "Illinois", "country": "United States", "point": {"lat": 39.78, "lng": -89.64}},
            {"name": "Springfield", "state": "Missouri", "country": "United States", "point": {"lat": 37.21, "lng": -93.29}},
        ]}
        with patch("requests.get", return_value=reply(data)) as get:
            matches = search_locations("Springfield")
        self.assertEqual(len(matches), 2)
        self.assertIn("Illinois", matches[0].label())
        self.assertIn("37.21000, -93.29000", matches[1].label())
        query = parse_qs(urlparse(get.call_args.args[0]).query)
        self.assertEqual(query["limit"], ["5"])
        self.assertEqual(query["q"], ["Springfield"])

    def test_no_matches_and_bad_location_data(self):
        with patch("requests.get", return_value=reply({"hits": []})):
            self.assertEqual(search_locations("unknown"), [])
        for data in ({}, {"hits": None}, {"hits": [{"name": "Bad", "point": {"lat": 95, "lng": 1}}]}):
            with self.subTest(data=data), patch("requests.get", return_value=reply(data)):
                with self.assertRaises(RoutingError):
                    search_locations("bad")

    def test_bad_match_is_skipped_and_search_is_biased(self):
        data = {"hits": [
            {"point": {"lat": 14.65, "lng": 121.03}},
            {"name": "SM North EDSA", "city": "Quezon City", "country": "Philippines",
             "point": {"lat": 14.6566, "lng": 121.0296}},
        ]}
        with patch("requests.get", return_value=reply(data)) as get:
            matches = search_locations("SM North EDSA", near=(14.6, 120.98))
        self.assertEqual([m.name for m in matches], ["SM North EDSA, Quezon City, Philippines"])
        query = parse_qs(urlparse(get.call_args.args[0]).query)
        self.assertEqual(query["point"], ["14.6,120.98"])

    def test_missing_key_stops_before_request(self):
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": ""}), patch("requests.get") as get,              patch("routing_service.ENV_FILE", os.path.join(os.path.dirname(__file__), "no-such.env")):
            with self.assertRaisesRegex(RoutingError, "GRAPHHOPPER_API_KEY"):
                search_locations("Manila")
            get.assert_not_called()

    def test_exact_miles_and_route_validation(self):
        origin = Location("Origin", 1, 2)
        destination = Location("Destination", 3, 4)
        data = {"paths": [{"distance": 1609.344, "time": 61000,
                           "instructions": [{"text": "Continue", "distance": 1609.344}]}]}
        with patch("requests.get", return_value=reply(data)):
            route = get_route(origin, destination, "bike")
        text = format_trip(origin, destination, "bike", "miles", route)
        self.assertIn("Distance Traveled: 1.0 miles", text)
        self.assertIn("1. Continue (1.0 miles)", text)
        self.assertIn("00:01:01", text)
        with patch("requests.get", return_value=reply({"paths": [{"distance": True, "time": 0, "instructions": []}]})):
            with self.assertRaisesRegex(RoutingError, "invalid route data"):
                get_route(origin, destination, "car")

    def test_route_details_include_map_geometry(self):
        origin = Location("Origin", 1, 2)
        destination = Location("Destination", 3, 4)
        data = {"paths": [{"distance": 2000, "time": 90000,
                           "points": {"type": "LineString", "coordinates": [[2, 1], [3, 2], [4, 3]]},
                           "instructions": [{"text": "Turn left", "distance": 1500, "sign": -2, "interval": [0, 1]},
                                            {"text": "Arrive", "distance": 0, "sign": 4, "interval": [2, 2]}]}]}
        with patch("requests.get", return_value=reply(data)) as get:
            route = get_route_details(origin, destination, "car")
        query = parse_qs(urlparse(get.call_args.args[0]).query)
        self.assertEqual(query["points_encoded"], ["false"])
        self.assertEqual(route.points, ((1, 2), (2, 3), (3, 4)))
        self.assertEqual(route.steps[0].sign, -2)
        self.assertEqual(route.step_points(0), ((1, 2), (2, 3)))
        self.assertEqual(route.bounds(), ((3, 2), (1, 4)))
        self.assertIn("1. Turn left (0.9 miles)", format_trip(origin, destination, "car", "miles", route))

    def test_route_without_geometry_falls_back_to_endpoints(self):
        origin = Location("Origin", 1, 2)
        destination = Location("Destination", 3, 4)
        data = {"paths": [{"distance": 10, "time": 1000,
                           "instructions": [{"text": "Go", "distance": 10, "interval": [0, 99]}]}]}
        with patch("requests.get", return_value=reply(data)):
            route = get_route_details(origin, destination, "foot")
        self.assertEqual(route.points, ((1, 2), (3, 4)))
        self.assertIsNone(route.steps[0].interval)

    def test_key_can_come_from_env_file(self):
        with tempfile.TemporaryDirectory() as folder:
            env_path = os.path.join(folder, ".env")
            with open(env_path, "w", encoding="utf-8") as env_file:
                env_file.write('# comment\nGRAPHHOPPER_API_KEY = "file-key"\n')
            with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": ""}), patch("routing_service.ENV_FILE", env_path):
                self.assertEqual(routing_service.api_key(), "file-key")

    def test_gui_formatters(self):
        self.assertEqual(format_distance(1609.344, "miles"), "1.0 mi")
        self.assertEqual(format_distance(2500, "kilometers"), "2.5 km")
        self.assertEqual(format_distance(50, "kilometers"), "50 m")
        self.assertEqual(format_duration(3_900_000), "1 h 05 min")
        self.assertEqual(format_duration(20_000), "1 min")

    def test_terminal_requires_selection_and_confirmation(self):
        results = [
            reply({"hits": [
                {"name": "First", "point": {"lat": 1, "lng": 2}},
                {"name": "Chosen", "point": {"lat": 3, "lng": 4}},
            ]}),
            reply({"hits": [{"name": "End", "point": {"lat": 5, "lng": 6}}]}),
            reply({"paths": [{"distance": 1609.344, "time": 1000,
                              "instructions": [{"text": "Arrive", "distance": 0}]}]}),
        ]
        answers = iter(["car", "m", "Start", "2", "n", "2", "y", "End", "1", "y", "q"])
        output = io.StringIO()
        with patch("builtins.input", side_effect=lambda _prompt: next(answers)), \
             patch("requests.get", side_effect=results) as get, contextlib.redirect_stdout(output):
            mapquest.main()
        self.assertEqual(get.call_count, 3)
        self.assertIn("From: Chosen", output.getvalue())
        query = parse_qs(urlparse(get.call_args.args[0]).query)
        self.assertEqual(query["point"], ["3,4", "5,6"])

    def test_terminal_research_and_quit(self):
        first = reply({"hits": [{"name": "Wrong", "point": {"lat": 1, "lng": 2}}]})
        second = reply({"hits": [{"name": "Right", "point": {"lat": 3, "lng": 4}}]})
        answers = iter(["Wrong", "r", "Right", "1", "q"])
        with patch("builtins.input", side_effect=lambda _prompt: next(answers)), \
             patch("requests.get", side_effect=[first, second]) as get:
            self.assertIsNone(mapquest.choose_location("Starting Location"))
        self.assertEqual(get.call_count, 2)



class OpenStreetMapFallbackTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": "test-key", "ROUTING_PROVIDER": "auto"})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.down = patch("routing_service._graphhopper_unreachable", False)
        self.down.start()
        self.addCleanup(self.down.stop)

    def osrm_reply(self):
        return reply({"code": "Ok", "routes": [{"distance": 1200, "duration": 300, "legs": [{"steps": [
            {"distance": 1200, "duration": 300, "name": "Roxas Boulevard",
             "maneuver": {"type": "depart", "bearing_after": 2},
             "geometry": {"coordinates": [[120.97, 14.58], [120.98, 14.59]]}},
            {"distance": 0, "duration": 0, "name": "", "maneuver": {"type": "turn", "modifier": "left"},
             "geometry": {"coordinates": [[120.98, 14.59], [120.99, 14.60]]}},
            {"distance": 0, "duration": 0, "name": "", "maneuver": {"type": "arrive"},
             "geometry": {"coordinates": [[120.99, 14.60], [120.99, 14.60]]}},
        ]}]}]})

    def test_unreachable_graphhopper_falls_back_to_openstreetmap(self):
        nominatim = reply([{"lat": "14.6566", "lon": "121.0296", "name": "SM North EDSA",
                            "address": {"city": "Quezon City", "country": "Philippines"}}])
        with patch("requests.get", side_effect=[requests.ConnectionError(), nominatim]) as get:
            matches = search_locations("SM North EDSA", near=(14.6, 120.98))
        self.assertEqual(matches[0].name, "SM North EDSA, Quezon City, Philippines")
        self.assertEqual(routing_service.last_provider, "osm")
        self.assertIn("nominatim.openstreetmap.org", get.call_args.args[0])
        self.assertIn("User-Agent", get.call_args.kwargs["headers"])
        # GraphHopper is not retried for the rest of the session.
        with patch("requests.get", return_value=self.osrm_reply()) as get:
            route = get_route_details(Location("A", 14.58, 120.97), Location("B", 14.60, 120.99), "bike")
        self.assertEqual(get.call_count, 1)
        self.assertIn("routed-bike", get.call_args.args[0])
        self.assertEqual([step.text for step in route.steps],
                         ["Head north on Roxas Boulevard", "Turn left", "Arrive at your destination"])
        self.assertEqual([step.sign for step in route.steps], [0, -2, 4])
        self.assertEqual(route.points, ((14.58, 120.97), (14.59, 120.98), (14.60, 120.99), (14.60, 120.99)))
        self.assertEqual(route.step_points(1), ((14.59, 120.98), (14.60, 120.99)))
        self.assertEqual(route.duration, 300000)

    def test_rejected_key_does_not_fall_back(self):
        with patch("requests.get", return_value=reply({}, 401)) as get:
            with self.assertRaisesRegex(RoutingError, "rejected"):
                search_locations("Manila")
        self.assertEqual(get.call_count, 1)

    def test_no_key_uses_openstreetmap_directly(self):
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": ""}),              patch("routing_service.ENV_FILE", os.path.join(os.path.dirname(__file__), "no-such.env")),              patch("requests.get", return_value=reply({"code": "NoRoute", "routes": []})) as get:
            with self.assertRaisesRegex(RoutingError, "No route found"):
                get_route_details(Location("A", 1, 2), Location("B", 3, 4), "car")
        self.assertIn("routing.openstreetmap.de", get.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
