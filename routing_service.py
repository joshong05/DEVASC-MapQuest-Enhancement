"""Shared routing requests and trip formatting for both interfaces.

GraphHopper is used when a key is set and graphhopper.com can be reached. Otherwise the
free OpenStreetMap services take over: Nominatim for place search, OSRM for routes.
Set ROUTING_PROVIDER to "graphhopper" or "osm" (environment or .env) to force one.
"""

import math
import os
from dataclasses import dataclass
from urllib.parse import urlencode

import requests


BASE_URL = "https://graphhopper.com/api/1"
NOMINATIM_URL = "https://nominatim.openstreetmap.org"
OSRM_URL = "https://routing.openstreetmap.de"
OSRM_PROFILES = {"car": "routed-car", "bike": "routed-bike", "foot": "routed-foot"}
OSM_HEADERS = {"User-Agent": "QuatroKantosRoutePlanner/1.0 (DEVASC school project)"}
PROVIDER_NAMES = {"graphhopper": "GraphHopper", "osm": "OpenStreetMap"}
METERS_PER_MILE = 1609.344
VEHICLES = ("car", "bike", "foot")


class RoutingError(Exception):
    """An error that can be shown directly to a user."""


class ConnectionFailure(RoutingError):
    """The service could not be reached at all (as opposed to rejecting the request)."""


@dataclass(frozen=True)
class Location:
    name: str
    lat: float
    lng: float

    def label(self):
        return f"{self.name} ({self.lat:.5f}, {self.lng:.5f})"


@dataclass(frozen=True)
class RouteStep:
    text: str
    distance: float
    time: float = 0
    sign: int = 0
    interval: tuple = None  # (first, last) index into Route.points, when known


@dataclass(frozen=True)
class Route:
    """A route with its drawable geometry. Iterating gives (distance, duration, steps)."""
    distance: float
    duration: float
    steps: tuple
    points: tuple  # ((lat, lng), ...)

    def __iter__(self):
        return iter((self.distance, self.duration, [(step.text, step.distance) for step in self.steps]))

    def bounds(self):
        """Return ((north, west), (south, east)) around every point."""
        lats = [lat for lat, _ in self.points]
        lngs = [lng for _, lng in self.points]
        return (max(lats), min(lngs)), (min(lats), max(lngs))

    def step_points(self, index):
        step = self.steps[index]
        if step.interval is None:
            return ()
        first, last = step.interval
        return self.points[first:last + 1]


ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _setting(name):
    """Read a setting from the environment, else from the git-ignored .env file."""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    try:
        with open(ENV_FILE, encoding="utf-8") as env_file:
            for line in env_file:
                key, separator, value = line.strip().partition("=")
                if separator and key.strip() == name:
                    return value.strip().strip("\"'")
    except OSError:
        pass
    return ""


def api_key():
    key = _setting("GRAPHHOPPER_API_KEY")
    if not key:
        raise RoutingError("Set GRAPHHOPPER_API_KEY (environment variable or .env file) before using the route planner.")
    return key


def _number(value, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError
    if minimum is not None and value < minimum:
        raise ValueError
    if maximum is not None and value > maximum:
        raise ValueError
    return value


# --- provider selection ---------------------------------------------------
_graphhopper_unreachable = False
last_provider = None  # "graphhopper" or "osm": whichever answered the latest request


def provider_mode():
    mode = _setting("ROUTING_PROVIDER").lower()
    return mode if mode in ("graphhopper", "osm") else "auto"


def _use_graphhopper():
    mode = provider_mode()
    if mode != "auto":
        return mode == "graphhopper"
    return not _graphhopper_unreachable and bool(_setting("GRAPHHOPPER_API_KEY"))


def current_provider_name():
    """The provider the next request will try first."""
    return PROVIDER_NAMES["graphhopper" if _use_graphhopper() else "osm"]


def _with_fallback(graphhopper_call, osm_call):
    global _graphhopper_unreachable, last_provider
    if _use_graphhopper():
        try:
            result = graphhopper_call()
            last_provider = "graphhopper"
            return result
        except ConnectionFailure:
            if provider_mode() == "graphhopper":
                raise
            _graphhopper_unreachable = True  # stop waiting on it for the rest of this session
    result = osm_call()
    last_provider = "osm"
    return result


# --- HTTP -----------------------------------------------------------------
GRAPHHOPPER_TIMEOUT = (4, 15)  # give up connecting quickly so the OpenStreetMap fallback starts fast


def _get_json(url, service, headers=None, timeout=15):
    try:
        if headers:
            reply = requests.get(url, timeout=timeout, headers=headers)
        else:
            reply = requests.get(url, timeout=timeout)
    except requests.RequestException:
        raise ConnectionFailure(f"{service} error: Could not connect. Check your connection and try again.") from None
    if reply.status_code != 200:
        if reply.status_code in (401, 403):
            raise RoutingError(f"{service} error: API key was rejected (HTTP {reply.status_code}).")
        if reply.status_code == 429:
            raise RoutingError(f"{service} error: Too many requests. Wait a moment and try again.")
        raise RoutingError(f"{service} error: Request failed (HTTP {reply.status_code}). Please try again.")
    try:
        return reply.json()
    except ValueError:
        raise RoutingError(f"{service} error: The service returned an invalid response.") from None


def _request(endpoint, parameters, service):
    data = _get_json(f"{BASE_URL}/{endpoint}?{urlencode(parameters)}", service, timeout=GRAPHHOPPER_TIMEOUT)
    if not isinstance(data, dict):
        raise RoutingError(f"{service} error: The service returned an invalid response.")
    return data


def search_locations(query, near=None):
    """Return up to five matches. `near` = (lat, lng) ranks places close to that point first."""
    if not query.strip():
        raise RoutingError("Enter a location to search.")
    return _with_fallback(lambda: _gh_search(query, near), lambda: _osm_search(query, near))


def reverse_geocode(lat, lng):
    """Return a Location named after the place nearest a map point, or a coordinate label."""
    return _with_fallback(lambda: _gh_reverse(lat, lng), lambda: _osm_reverse(lat, lng))


def get_route(origin, destination, vehicle):
    """Return (distance, duration, steps); see get_route_details for map geometry."""
    return tuple(get_route_details(origin, destination, vehicle))


def get_route_details(origin, destination, vehicle):
    if vehicle not in VEHICLES:
        raise RoutingError("Choose car, bike, or foot.")
    return _with_fallback(lambda: _gh_route(origin, destination, vehicle),
                          lambda: _osm_route(origin, destination, vehicle))


# --- GraphHopper ----------------------------------------------------------
def _gh_search(query, near):
    parameters = {"q": query, "limit": 5, "key": api_key()}
    if near is not None:
        parameters["point"] = f"{near[0]},{near[1]}"
    data = _request("geocode", parameters, "Location search")
    hits = data.get("hits")
    if not isinstance(hits, list):
        raise RoutingError("Location search error: The service returned incomplete location data.")
    locations = []
    for hit in hits:
        try:
            point = hit["point"]
            lat = _number(point["lat"], -90, 90)
            lng = _number(point["lng"], -180, 180)
            parts = []
            for field in ("name", "street", "city", "state", "country"):
                part = hit.get(field)
                if isinstance(part, str) and part.strip() and part.strip() not in parts:
                    parts.append(part.strip())
            if not parts:
                raise ValueError
            locations.append(Location(", ".join(parts), lat, lng))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue  # skip one bad match instead of losing every result
    if hits and not locations:
        raise RoutingError("Location search error: The service returned incomplete or invalid location data.")
    return locations


def _gh_reverse(lat, lng):
    fallback = Location(f"Dropped pin {lat:.5f}, {lng:.5f}", lat, lng)
    try:
        data = _request("geocode", {"point": f"{lat},{lng}", "reverse": "true", "limit": 1, "key": api_key()},
                        "Location search")
        hit = data["hits"][0]
        parts = []
        for field in ("name", "street", "city", "country"):
            part = hit.get(field)
            if isinstance(part, str) and part.strip() and part.strip() not in parts:
                parts.append(part.strip())
        return Location(", ".join(parts), lat, lng) if parts else fallback
    except RoutingError:
        raise
    except (KeyError, IndexError, TypeError):
        return fallback


def _route_points(path, origin, destination):
    try:
        coordinates = path["points"]["coordinates"]
        points = tuple((_number(c[1], -90, 90), _number(c[0], -180, 180)) for c in coordinates)
        if len(points) >= 2:
            return points
    except (KeyError, IndexError, TypeError, ValueError):
        pass
    return (origin.lat, origin.lng), (destination.lat, destination.lng)


def _step_interval(step, point_count):
    interval = step.get("interval")
    if (isinstance(interval, list) and len(interval) == 2
            and all(isinstance(i, int) and not isinstance(i, bool) for i in interval)
            and 0 <= interval[0] <= interval[1] < point_count):
        return tuple(interval)
    return None


def _gh_route(origin, destination, vehicle):
    data = _request("route", [
        ("key", api_key()), ("vehicle", vehicle),
        ("point", f"{origin.lat},{origin.lng}"),
        ("point", f"{destination.lat},{destination.lng}"),
        ("points_encoded", "false"),
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
        points = _route_points(path, origin, destination)
        steps = []
        for step in instructions:
            direction = step["text"]
            if not isinstance(direction, str) or not direction.strip():
                raise ValueError
            sign = step.get("sign", 0)
            time = step.get("time", 0)
            steps.append(RouteStep(
                direction.strip(), _number(step["distance"], 0),
                time if isinstance(time, (int, float)) and not isinstance(time, bool) else 0,
                sign if isinstance(sign, int) and not isinstance(sign, bool) else 0,
                _step_interval(step, len(points)),
            ))
    except (KeyError, IndexError, TypeError, ValueError):
        raise RoutingError("Routing error: The service returned incomplete or invalid route data.") from None
    return Route(distance, duration, tuple(steps), points)


# --- OpenStreetMap (Nominatim + OSRM) ---------------------------------------
def _osm_place_name(hit):
    address = hit.get("address") if isinstance(hit.get("address"), dict) else {}
    candidates = [hit.get("name"), address.get("road"),
                  address.get("city") or address.get("town") or address.get("municipality") or address.get("village"),
                  address.get("state") or address.get("region"), address.get("country")]
    parts = []
    for part in candidates:
        if isinstance(part, str) and part.strip() and part.strip() not in parts:
            parts.append(part.strip())
    if len(parts) < 2 and isinstance(hit.get("display_name"), str):
        parts = [part.strip() for part in hit["display_name"].split(",") if part.strip()][:4]
    return ", ".join(parts)


def _osm_search(query, near):
    parameters = {"q": query, "format": "jsonv2", "limit": 5, "addressdetails": 1}
    if near is not None:  # prefer, but do not restrict to, the visible area
        lat, lng = near
        parameters["viewbox"] = f"{lng - 0.5},{lat + 0.5},{lng + 0.5},{lat - 0.5}"
    data = _get_json(f"{NOMINATIM_URL}/search?{urlencode(parameters)}", "Location search", OSM_HEADERS)
    if not isinstance(data, list):
        raise RoutingError("Location search error: The service returned incomplete location data.")
    locations = []
    for hit in data:
        try:
            lat = _number(float(hit["lat"]), -90, 90)
            lng = _number(float(hit["lon"]), -180, 180)
            name = _osm_place_name(hit)
            if not name:
                raise ValueError
            locations.append(Location(name, lat, lng))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    if data and not locations:
        raise RoutingError("Location search error: The service returned incomplete or invalid location data.")
    return locations


def _osm_reverse(lat, lng):
    fallback = Location(f"Dropped pin {lat:.5f}, {lng:.5f}", lat, lng)
    parameters = {"lat": lat, "lon": lng, "format": "jsonv2", "addressdetails": 1}
    data = _get_json(f"{NOMINATIM_URL}/reverse?{urlencode(parameters)}", "Location search", OSM_HEADERS)
    name = _osm_place_name(data) if isinstance(data, dict) and "error" not in data else ""
    return Location(name, lat, lng) if name else fallback


_TURN_SIGNS = {"uturn": -98, "sharp left": -3, "left": -2, "slight left": -1, "straight": 0,
               "slight right": 1, "right": 2, "sharp right": 3}
_COMPASS = ("north", "northeast", "east", "southeast", "south", "southwest", "west", "northwest")


def _osrm_instruction(step):
    """Build GraphHopper-style text and a turn sign from an OSRM maneuver."""
    maneuver = step.get("maneuver") or {}
    kind = maneuver.get("type", "")
    modifier = maneuver.get("modifier", "") or ""
    road = step.get("name") or step.get("ref") or ""
    onto = f" onto {road}" if road else ""
    side = "left" if "left" in modifier else "right"
    sign = _TURN_SIGNS.get(modifier, 0)
    if kind == "depart":
        heading = _COMPASS[round((maneuver.get("bearing_after") or 0) / 45) % 8]
        return f"Head {heading}" + (f" on {road}" if road else ""), 0
    if kind == "arrive":
        where = f" on the {modifier}" if modifier in ("left", "right") else ""
        return f"Arrive at your destination{where}", 4
    if kind in ("roundabout", "rotary"):
        exit_number = maneuver.get("exit")
        if exit_number:
            return f"At the roundabout, take exit {exit_number}{onto}", 6
        return f"Enter the roundabout{onto}", 6
    if kind in ("exit roundabout", "exit rotary"):
        return f"Exit the roundabout{onto}", 0
    if kind == "fork":
        return f"Keep {side} at the fork{onto}", -7 if side == "left" else 7
    if kind in ("on ramp", "off ramp"):
        return f"Take the ramp on the {side}{onto}", -7 if side == "left" else 7
    if kind == "merge":
        return (f"Merge {side}{onto}" if modifier else f"Merge{onto}"), sign
    if kind == "end of road" and modifier:
        return f"At the end of the road, turn {modifier}{onto}", sign
    if modifier == "uturn":
        return f"Make a U-turn{onto}", -98
    if modifier in ("straight", ""):
        return (f"Continue onto {road}" if road else "Continue straight"), 0
    if modifier.startswith("slight"):
        return f"Bear {side}{onto}", sign
    return f"Turn {modifier}{onto}", sign


def _osm_route(origin, destination, vehicle):
    url = (f"{OSRM_URL}/{OSRM_PROFILES[vehicle]}/route/v1/driving/"
           f"{origin.lng},{origin.lat};{destination.lng},{destination.lat}"
           "?overview=false&steps=true&geometries=geojson")
    data = _get_json(url, "Routing", OSM_HEADERS)
    if not isinstance(data, dict):
        raise RoutingError("Routing error: The service returned an invalid response.")
    if data.get("code") in ("NoRoute", "NoSegment") or data.get("routes") == []:
        raise RoutingError("No route found. Try different locations or another vehicle profile.")
    if data.get("code") != "Ok":
        raise RoutingError("Routing error: The service returned incomplete route data.")
    try:
        route = data["routes"][0]
        distance = _number(route["distance"], 0)
        duration = _number(route["duration"], 0) * 1000
        points, steps = [], []
        for leg in route["legs"]:
            for step in leg["steps"]:
                coordinates = [(_number(c[1], -90, 90), _number(c[0], -180, 180))
                               for c in step["geometry"]["coordinates"]]
                # Each step starts where the previous one ended; share that point.
                if points and coordinates and coordinates[0] == points[-1]:
                    first = len(points) - 1
                    coordinates = coordinates[1:]
                else:
                    first = len(points)
                points.extend(coordinates)
                last = max(first, len(points) - 1)
                text, sign = _osrm_instruction(step)
                steps.append(RouteStep(text, _number(step["distance"], 0), _number(step["duration"], 0) * 1000,
                                       sign, (first, last) if last < len(points) else None))
        if not steps:
            raise ValueError
    except (KeyError, IndexError, TypeError, ValueError):
        raise RoutingError("Routing error: The service returned incomplete or invalid route data.") from None
    if len(points) < 2:
        points = [(origin.lat, origin.lng), (destination.lat, destination.lng)]
        steps = [RouteStep(step.text, step.distance, step.time, step.sign, None) for step in steps]
    return Route(distance, duration, tuple(steps), tuple(points))


def convert_distance(meters, unit):
    """Convert meters to miles or kilometers."""
    return meters / (1000 if unit == "kilometers" else METERS_PER_MILE)


def format_distance(meters, unit):
    short = "km" if unit == "kilometers" else "mi"
    value = convert_distance(meters, unit)
    if value < 0.1 and meters > 0:
        return f"{meters:.0f} m" if unit == "kilometers" else f"{meters / 0.3048:.0f} ft"
    return f"{value:.1f} {short}"


def format_duration(milliseconds):
    minutes = round(milliseconds / 60000)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours} h {minutes:02d} min"
    return f"{max(minutes, 1) if milliseconds else 0} min"


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
