"""Mocked API checks for the shared routing code and location selection."""

import contextlib
import io
import os
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import mapquest
from routing_service import Location, RoutingError, format_trip, get_route, search_locations


def reply(data, status=200):
    return Mock(status_code=status, json=Mock(return_value=data))


class RoutingServiceTests(unittest.TestCase):
    def setUp(self):
        self.key = patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": "test-key"})
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

    def test_missing_key_stops_before_request(self):
        with patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": ""}), patch("requests.get") as get:
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


if __name__ == "__main__":
    unittest.main()
