import math
import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"
key = "4fd861c0-4509-4102-8d21-fdb75d9001e0"


def read_input(prompt):
    """Reject blank input and allow quitting at any prompt."""
    while True:
        value = input(prompt).strip()
        if value.lower() in ("q", "quit"):
            return None
        if value:
            return value
        print("Please enter a value, or type q to quit.")


def request_json(url, service):
    """Return API data, or explain why the request could not be completed."""
    try:
        response = requests.get(url, timeout=15)
    except requests.RequestException:
        print(f"{service} error: Could not connect. Check your connection and try again.")
        return None

    if response.status_code != 200:
        print(f"{service} error: Request failed (HTTP {response.status_code}). Please try again.")
        return None

    try:
        data = response.json()
    except ValueError:
        print(f"{service} error: The service returned an invalid response. Please try again.")
        return None
    if not isinstance(data, dict):
        print(f"{service} error: The service returned an invalid response. Please try again.")
        return None
    return data


def geocoding(location, key):
    geocode_url = "https://graphhopper.com/api/1/geocode?"
    url = geocode_url + urllib.parse.urlencode({
        "q": location,
        "limit": "1",
        "key": key
    })
    data = request_json(url, "Location search")
    if data is None:
        return None

    try:
        hits = data["hits"]
        if not isinstance(hits, list):
            raise ValueError
        if not hits:
            print(f"Location not found: {location}. Check the spelling or add a city/country.")
            return None
        hit = hits[0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        if not math.isfinite(lat) or not math.isfinite(lng) or not (-90 <= lat <= 90 and -180 <= lng <= 180):
            raise ValueError
        new_loc = ", ".join(part for part in (hit["name"], hit.get("state"), hit.get("country")) if part)
    except (KeyError, IndexError, TypeError, ValueError):
        print("Location search error: The service returned incomplete or invalid location data.")
        return None

    print(f"Location found: {new_loc}")
    return lat, lng, new_loc


while True:
    print("\n" + "=" * 49)
    print("MAPQUEST ROUTE PLANNER - GraphHopper")
    print("=" * 49)
    print("Vehicle profiles: car, bike, foot")
    print("Type q or quit at any prompt to exit.")

    vehicle = read_input("Vehicle profile: ")
    if vehicle is None:
        break
    vehicle = vehicle.lower()
    if vehicle not in ("car", "bike", "foot"):
        print("Invalid vehicle profile. Please choose car, bike, or foot.")
        continue

    unit_choice = input("Choose distance unit [m]iles or [k]ilometers (default miles): ").strip().lower()
    if unit_choice in ("q", "quit"):
        break
    if unit_choice not in ("", "m", "miles", "k", "kilometers"):
        print("Invalid distance unit. Please choose miles (m) or kilometers (k).")
        continue
    unit_name = "kilometers" if unit_choice in ("k", "kilometers") else "miles"
    multiplier = 1.60934 if unit_name == "kilometers" else 1.0

    loc1 = read_input("Starting Location: ")
    if loc1 is None:
        break
    orig = geocoding(loc1, key)
    if orig is None:
        continue

    loc2 = read_input("Destination: ")
    if loc2 is None:
        break
    dest = geocoding(loc2, key)
    if dest is None:
        continue

    paths_url = route_url + urllib.parse.urlencode([
        ("key", key),
        ("vehicle", vehicle),
        ("point", f"{orig[0]},{orig[1]}"),
        ("point", f"{dest[0]},{dest[1]}")
    ])
    paths_data = request_json(paths_url, "Routing")
    if paths_data is None:
        continue

    try:
        paths = paths_data["paths"]
        if not isinstance(paths, list):
            raise ValueError
        if not paths:
            print("No route found. Try different locations or another vehicle profile.")
            continue
        route = paths[0]
        distance = route["distance"]
        duration = route["time"]
        instructions = route["instructions"]
        if not math.isfinite(distance) or not math.isfinite(duration) or distance < 0 or duration < 0:
            raise ValueError
        if not isinstance(instructions, list) or not instructions:
            raise ValueError
        for instruction in instructions:
            if not isinstance(instruction["text"], str) or not instruction["text"].strip():
                raise ValueError
            if not math.isfinite(instruction["distance"]) or instruction["distance"] < 0:
                raise ValueError
    except (KeyError, IndexError, TypeError, ValueError):
        print("Routing error: The service returned incomplete or invalid route data. Please try again.")
        continue

    miles = distance / 1000 / 1.61
    sec = int(duration / 1000 % 60)
    min = int(duration / 1000 / 60 % 60)
    hr = int(duration / 1000 / 60 / 60)

    print("\n" + "=" * 49)
    print("TRIP SUMMARY")
    print("=" * 49)
    print(f"From: {orig[2]}")
    print(f"To: {dest[2]}")
    print(f"Vehicle: {vehicle}")
    print("Distance Traveled: {0:.1f} {1}".format(miles * multiplier, unit_name))
    print("Trip Duration: {0:02d}:{1:02d}:{2:02d}".format(hr, min, sec))
    print("-" * 49)
    print("DIRECTIONS")
    for number, instruction in enumerate(instructions, start=1):
        print("{0}. {1} ({2:.1f} {3})".format(
            number,
            instruction["text"],
            (instruction["distance"] / 1000 / 1.61) * multiplier,
            unit_name
        ))
    print("=" * 49)

print("Goodbye!")
