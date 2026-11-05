"""Run with: python -m unittest discover -s tests -v"""
import contextlib
import io
import os
from pathlib import Path
import runpy
import unittest
from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlparse

import requests


APP = Path(__file__).resolve().parents[1] / "mapquest.py"


def response(data=None, status=200, invalid_json=False):
    reply = Mock(status_code=status)
    reply.json = Mock(side_effect=ValueError("invalid JSON")) if invalid_json else Mock(return_value=data)
    return reply


def location(name="Manila", lat=14.6, lng=121.0):
    return response({"hits": [{"point": {"lat": lat, "lng": lng}, "name": name, "country": "Philippines"}]})


def route(**changes):
    data = {"distance": 16100, "time": 900000, "instructions": [{"text": "Turn right", "distance": 8050}]}
    data.update(changes)
    return response({"paths": [data]})


class MapQuestTests(unittest.TestCase):
    def run_app(self, inputs, replies):
        output = io.StringIO()
        answers = iter(inputs)

        def answer(prompt):
            if prompt.startswith("Number or r"):
                return "1"
            if prompt.startswith("Confirm?"):
                return "y"
            return next(answers)

        with patch("builtins.input", side_effect=answer), patch.dict(os.environ, {"GRAPHHOPPER_API_KEY": "test-key", "ROUTING_PROVIDER": "graphhopper"}), patch("requests.get", side_effect=replies) as get, contextlib.redirect_stdout(output):
            runpy.run_path(str(APP), run_name="__main__")
        text = output.getvalue()
        self.assertIn("Goodbye!", text)
        self.assertNotIn("key=", text)
        for call in get.call_args_list:
            self.assertEqual(call.kwargs["timeout"], (4, 15))
        return text, get

    def test_unit_selection_and_vehicle_profiles(self):
        for unit in ("m", "miles", "", "k", "kilometers", " K "):
            for vehicle in ("car", "bike", "foot"):
                with self.subTest(unit=unit, vehicle=vehicle):
                    text, get = self.run_app([vehicle.upper(), unit, "Manila", "Quezon City", "q"], [location(), location("Quezon City", 14.65, 121.05), route()])
                    metric = unit.strip().lower() in ("k", "kilometers")
                    self.assertIn("Distance Traveled: " + ("16.1 kilometers" if metric else "10.0 miles"), text)
                    self.assertIn("1. Turn right (" + ("8.1 kilometers" if metric else "5.0 miles") + ")", text)
                    self.assertIn("TRIP SUMMARY", text)
                    self.assertIn("DIRECTIONS", text)
                    self.assertIn("Trip Duration: 00:15:00", text)
                    self.assertEqual(get.call_count, 3)
                    query = parse_qs(urlparse(get.call_args_list[-1].args[0]).query)
                    self.assertEqual(query["vehicle"], [vehicle])
                    self.assertEqual(query["point"], ["14.6,121.0", "14.65,121.05"])

    def test_exact_conversion_factor(self):
        text, _ = self.run_app(["car", "k", "Manila", "Quezon City", "q"], [location(), location(), route(distance=1610000, instructions=[{"text": "Continue", "distance": 805000}])])
        self.assertIn("Distance Traveled: 1610.0 kilometers", text)
        self.assertIn("1. Continue (805.0 kilometers)", text)

    def test_invalid_selections_make_no_requests(self):
        for inputs, expected in [(["plane", "q"], "Invalid vehicle profile"), (["car", "yards", "q"], "Invalid distance unit")]:
            with self.subTest(inputs=inputs):
                text, get = self.run_app(inputs, [])
                self.assertIn(expected, text)
                get.assert_not_called()

    def test_blank_locations_reprompt(self):
        text, get = self.run_app([" ", "car", "m", " ", "Manila", " ", "Quezon City", "q"], [location(), location("Quezon City"), route()])
        self.assertEqual(text.count("Please enter a value"), 3)
        self.assertEqual(get.call_count, 3)

    def test_quit_at_each_prompt(self):
        for inputs, replies in [([" QUIT "], []), (["car", "Q"], []), (["car", "m", "q"], []), (["car", "k", "Manila", "quit"], [location()])]:
            with self.subTest(inputs=inputs):
                _, get = self.run_app(inputs, replies)
                self.assertEqual(get.call_count, len(replies))

    def test_geocoding_failures_do_not_request_routes(self):
        failures = [response({"hits": []}), response({}, 401), response(invalid_json=True), response([]), response({}), response({"hits": None}), location(lat=None), requests.Timeout(), requests.ConnectionError()]
        for failure in failures:
            with self.subTest(failure=failure):
                text, get = self.run_app(["car", "m", "Manila", "q"], [failure])
                self.assertTrue("Location not found:" in text or "error:" in text)
                self.assertNotIn("TRIP SUMMARY", text)
                self.assertEqual(get.call_count, 1)

    def test_invalid_route_responses(self):
        failures = [response({}, 500), response(invalid_json=True), response([]), response({}), response({"paths": []}), response({"paths": None}), response({"paths": [{}]}), route(distance=-1), route(distance=float("nan")), route(time="bad"), route(instructions=[]), route(instructions=[{"text": "Bad"}]), requests.Timeout()]
        for failure in failures:
            with self.subTest(failure=failure):
                text, get = self.run_app(["car", "k", "Manila", "Quezon City", "q"], [location(), location(), failure])
                self.assertTrue("Routing error:" in text or "No route found" in text)
                self.assertNotIn("TRIP SUMMARY", text)
                self.assertEqual(get.call_count, 3)

    def test_recovery_and_unit_change_after_error(self):
        text, get = self.run_app(["car", "m", "Manila", "Quezon City", "bike", "k", "Manila", "Quezon City", "q"], [location(), location(), response({}, 500), location(), location(), route()])
        self.assertIn("Routing error:", text)
        self.assertIn("Vehicle: bike", text)
        self.assertIn("Distance Traveled: 16.1 kilometers", text)
        self.assertEqual(get.call_count, 6)


if __name__ == "__main__":
    unittest.main()
