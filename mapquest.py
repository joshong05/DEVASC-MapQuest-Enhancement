"""Terminal route planner. Run with: python mapquest.py"""

from routing_service import RoutingError, VEHICLES, format_trip, get_route, search_locations


def read_input(prompt, allow_blank=False):
    while True:
        try:
            value = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            return None
        if value.lower() in ("q", "quit"):
            return None
        if value or allow_blank:
            return value
        print("Please enter a value, or type q to quit.")


def choose_location(label):
    while True:
        query = read_input(f"{label}: ")
        if query is None:
            return None
        try:
            matches = search_locations(query)
        except RoutingError as error:
            print(error)
            continue
        if not matches:
            print(f"Location not found: {query}. Check spelling or add a city/country.")
            continue
        print("Select the correct location:")
        for number, match in enumerate(matches, 1):
            print(f"{number}. {match.label()}")
        while True:
            choice = read_input("Number or r to re-search: ")
            if choice is None:
                return None
            if choice.lower() == "r":
                break
            if not choice.isdigit() or not 1 <= int(choice) <= len(matches):
                print("Enter a listed number or r to re-search.")
                continue
            selected = matches[int(choice) - 1]
            print(f"Selected: {selected.label()}")
            confirmation = read_input("Confirm? [y]es, [n]o, [r]e-search: ")
            if confirmation is None:
                return None
            if confirmation.lower() in ("y", "yes"):
                return selected
            if confirmation.lower() == "r":
                break
            if confirmation.lower() not in ("n", "no"):
                print("Enter y, n, or r.")


def main():
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
        if vehicle not in VEHICLES:
            print("Invalid vehicle profile. Please choose car, bike, or foot.")
            continue
        choice = read_input("Choose distance unit [m]iles or [k]ilometers (default miles): ", allow_blank=True)
        if choice is None:
            break
        choice = choice.lower()
        if choice not in ("", "m", "miles", "k", "kilometers"):
            print("Invalid distance unit. Please choose miles (m) or kilometers (k).")
            continue
        unit = "kilometers" if choice in ("k", "kilometers") else "miles"
        origin = choose_location("Starting Location")
        if origin is None:
            break
        destination = choose_location("Destination")
        if destination is None:
            break
        try:
            route = get_route(origin, destination, vehicle)
            print("\n" + format_trip(origin, destination, vehicle, unit, route))
        except RoutingError as error:
            print(error)
    print("Goodbye!")


if __name__ == "__main__":
    main()
