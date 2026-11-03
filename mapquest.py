import urllib.parse
import requests

# Standard MapQuest base URL
url = "https://www.mapquestapi.com/directions/v2/route?"

while True:
    orig = input("Starting Location (or type 'quit' to exit): ").strip()
    if orig.lower() == "quit":
        break
    dest = input("Destination: ").strip()
    if dest.lower() == "quit":
        break
    
    # Input validation for empty fields
    if not orig or not dest:
        print("\n[Error] Starting location and destination cannot be empty. Please try again.\n")
        continue

    # Prompt user for distance unit preference
    unit_choice = input("Choose distance unit [m]iles or [k]ilometers (default miles): ").lower()
    if unit_choice == 'k':
        unit_name = "kilometers"
        multiplier = 1.60934
    else:
        unit_name = "miles"
        multiplier = 1.0

    # Simulated MapQuest API response for offline testing
    json_data = {
        "info": {"statuscode": 0},
        "route": {
            "distance": 10.0,  # Base distance in miles
            "formattedTime": "00:25:00",
            "legs": [
                {
                    "maneuvers": [
                        {"narrative": "Start out going north on Main St."},
                        {"narrative": "Turn right onto Grand Ave. Destination will be on the right."}
                    ]
                }
            ]
        }
    }
    
    # Basic parsing with unit conversion and clear display
    if json_data["info"]["statuscode"] == 0:
        print("\n========================================")
        print("API Status: 0 = Successful retrieval")
        
        # Calculate distance based on user choice
        base_distance = json_data["route"]["distance"]
        converted_distance = base_distance * multiplier
        
        print(f"Distance: {converted_distance:.2f} {unit_name}")
        print("Trip Duration: " + str(json_data["route"]["formattedTime"]))
        print("-" * 40)
        
        for maneuver in json_data["route"]["legs"][0]["maneuvers"]:
            print(f"- {maneuver['narrative']}")
        print("========================================\n")
    else:
        print("\n****************************************")
        print("Error processing request. Status code:", json_data["info"]["statuscode"])
        print("****************************************\n")