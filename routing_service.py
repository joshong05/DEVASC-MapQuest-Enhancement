"""Shared GraphHopper requests and trip formatting for both interfaces."""

import math
import os
from dataclasses import dataclass
from urllib.parse import urlencode

import requests


BASE_URL = "https://graphhopper.com/api/1"
METERS_PER_MILE = 1609.344
VEHICLES = ("car", "bike", "foot")


class RoutingError(Exception):
    """An error that can be shown directly to a user."""


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lng: float

    def label(self):
        return f"{self.name} ({self.lat:.5f}, {self.lng:.5f})"


def api_key():
    key = os.environ.get("GRAPHHOPPER_API_KEY", "").strip()
    if not key:
        raise RoutingError("Set GRAPHHOPPER_API_KEY before using the route planner.")
    return key


def _number(value, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError
    if minimum is not None and value < minimum:
        raise ValueError
    if maximum is not None and value > maximum:
        raise ValueError
    return value


def _request(endpoint, parameters, service):
    url = f"{BASE_URL}/{endpoint}?{urlencode(parameters)}"
    try:
        reply = requests.get(url, timeout=15)
    except requests.RequestException:
        raise RoutingError(f"{service} error: Could not connect. Check your connection and try again.") from None
    if reply.status_code != 200:
        if reply.status_code in (401, 403):
            raise RoutingError(f"{service} error: API key was rejected (HTTP {reply.status_code}).")
        raise RoutingError(f"{service} error: Request failed (HTTP {reply.status_code}). Please try again.")
    try:
        data = reply.json()
    except ValueError:
        raise RoutingError(f"{service} error: The service returned an invalid response.") from None
    if not isinstance(data, dict):
        raise RoutingError(f"{service} error: The service returned an invalid response.")
    return data


def search_locations(query):
    if not query.strip():
        raise RoutingError("Enter a location to search.")
    data = _request("geocode", {"q": query, "limit": 5, "key": api_key()}, "Location search")
    hits = data.get("hits")
    if not isinstance(hits, list):
        raise RoutingError("Location search error: The service returned incomplete location data.")
    locations = []
    for hit in hits:
        try:
            point = hit["point"]
            lat = _number(point["lat"], -90, 90)
            lng = _number(point["lng"], -180, 180)
            name = hit["name"]
            if not isinstance(name, str) or not name.strip():
                raise ValueError
            parts = [name.strip()]
            for field in ("city", "state", "country"):
                part = hit.get(field)
                if isinstance(part, str) and part.strip() and part.strip() not in parts:
                    parts.append(part.strip())
            locations.append(Location(", ".join(parts), lat, lng))
        except (KeyError, TypeError, ValueError):
            raise RoutingError("Location search error: The service returned incomplete or invalid location data.") from None
    return locations


def get_route(origin, destination, vehicle):
    if vehicle not in VEHICLES:
        raise RoutingError("Choose car, bike, or foot.")
    data = _request("route", [
        ("key", api_key()), ("vehicle", vehicle),
        ("point", f"{origin.lat},{origin.lng}"),
        ("point", f"{destination.lat},{destination.lng}"),
    ], "Routing")
    paths = data.get("paths")
    if not isinstance(paths, list):
        raise RoutingError("Routing error: The service returned incomplete route data.")
    if not paths:
        raise RoutingError("No route found. Try different locations or another vehicle profile.")
    try:
        path = paths[0]
        distance = _number(path["distance"], 0)
        duration = _number(path["time"], 0)
        instructions = path["instructions"]
        if not isinstance(instructions, list) or not instructions:
            raise ValueError
        steps = []
        for step in instructions:
            direction = step["text"]
            if not isinstance(direction, str) or not direction.strip():
                raise ValueError
            steps.append((direction.strip(), _number(step["distance"], 0)))
    except (KeyError, IndexError, TypeError, ValueError):
        raise RoutingError("Routing error: The service returned incomplete or invalid route data.") from None
    return distance, duration, steps


def format_trip(origin, destination, vehicle, unit, route):
    distance, duration, steps = route
    unit_name = "kilometers" if unit == "kilometers" else "miles"
    divisor = 1000 if unit_name == "kilometers" else METERS_PER_MILE
    total_seconds = int(duration / 1000)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    lines = [
        "=" * 49, "TRIP SUMMARY", "=" * 49,
        f"From: {origin.name}", f"To: {destination.name}",
        f"Vehicle: {vehicle}",
        f"Distance Traveled: {distance / divisor:.1f} {unit_name}",
        f"Trip Duration: {hours:02d}:{minutes:02d}:{seconds:02d}",
        "-" * 49, "DIRECTIONS",
    ]
    lines.extend(f"{number}. {direction} ({length / divisor:.1f} {unit_name})"
                 for number, (direction, length) in enumerate(steps, 1))
    lines.append("=" * 49)
    return "\n".join(lines)
