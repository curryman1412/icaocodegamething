import os
import math

import escape_db


# Game settings
BATTERY = 100
distance = 0

# Starting airport
START_AIRPORT = "EFHK"

# London Heathrow
GOAL_AIRPORT = "EGLL"


# Clear screen
def clear():
    os.system("cls" if os.name == "nt" else "clear")


# Starting menu
def prompt():
    print("\t\tICAO AIRPORT ADVENTURE\n")
    print("You are flying an electric aircraft.")
    print("Your goal is to reach London Heathrow.")
    print("You must manage your battery during the journey.")
    print()
    print("Commands:")
    print("  fly {airport}  - travel to an airport")
    print("  status         - show your current status")
    print("  map            - show available airports")
    print("  help           - show commands")
    print("  exit           - quit the game")
    print()
    input("Press Enter to start...")


# Calculate distance
def calculate_distance(lat1, lon1, lat2, lon2):
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    earth_radius = 6371

    return earth_radius * c


# Find destination
def find_destination(user_input):
    search = user_input.strip()

    airport = escape_db.get_airport(search)

    if airport is not None:
        return airport

    airports = escape_db.find_airport(search)

    if len(airports) == 1:
        return airports[0]

    if len(airports) == 0:
        return None

    print()
    print("Several airports match your search:")
    print()

    for airport in airports:
        print(f"{airport[0]} - {airport[1]}")

    print()

    choice = input("Enter the airport code you want: ")

    return escape_db.get_airport(choice)


# Show current airport
def show_airport(airport):
    print(f"Current airport: {airport[0]}")
    print(f"Airport: {airport[1]}")
    print(f"Country: {airport[4]}")
    print(f"Latitude: {airport[2]}")
    print(f"Longitude: {airport[3]}")
    print(f"Battery: {BATTERY}%")
    print(f"Distance travelled: {distance:.0f} km")
    print("-" * 40)


# Show nearby airports
def show_map(current_airport):

    print()
    print("========== NEARBY AIRPORTS ==========")
    print()

    airports = escape_db.get_nearby_airports(
        current_airport[2],
        current_airport[3]
    )

    airports_with_distance = []

    for airport in airports:

        # Don't show current airport
        if airport[0].upper() == current_airport[0].upper():
            continue

        flight_distance = calculate_distance(
            current_airport[2],
            current_airport[3],
            airport[2],
            airport[3]
        )

        # Calculate battery needed
        battery_cost = math.ceil(
            flight_distance / 100 * 5
        )

        if battery_cost < 1:
            battery_cost = 1

        # Only show airports that can be reached
        if battery_cost <= BATTERY:
            airports_with_distance.append(
                (airport, flight_distance, battery_cost)
            )

    # Sort airports by distance
    airports_with_distance.sort(
        key=lambda item: item[1]
    )

    # Show 10 closest reachable airports
    for airport, flight_distance, battery_cost in airports_with_distance[:10]:

        print(f"{airport[0]} - {airport[1]}")
        print(f"    Distance: {flight_distance:.0f} km")
        print(f"    Battery required: {battery_cost}%")
        print()

    if not airports_with_distance:
        print("There are no reachable airports with your current battery.")

    print("====================================")
    print()


# Show status
def show_status(current_airport):
    print()
    print("========== STATUS ==========")
    print(f"Airport: {current_airport[1]}")
    print(f"Code: {current_airport[0]}")
    print(f"Country: {current_airport[4]}")
    print(f"Battery: {BATTERY}%")
    print(f"Distance travelled: {distance:.0f} km")
    print("============================")
    print()


# Fly to another airport
def fly(destination, current_airport):
    global BATTERY
    global distance

    destination_airport = find_destination(destination)

    if destination_airport is None:
        return (
            current_airport,
            "That airport does not exist."
        )

    if destination_airport[0].lower() == current_airport[0].lower():
        return (
            current_airport,
            "You are already at that airport."
        )

    flight_distance = calculate_distance(
        current_airport[2],
        current_airport[3],
        destination_airport[2],
        destination_airport[3]
    )

    # Calculate battery consumption
    battery_cost = math.ceil(
        flight_distance / 100 * 5
    )

    # Short flights use at least 1% battery
    if battery_cost < 1:
        battery_cost = 1

    # Check if there is enough battery
    if battery_cost > BATTERY:
        return (
            current_airport,
            f"Not enough battery. "
            f"This flight requires "
            f"{battery_cost}% battery."
        )

    # Complete flight
    BATTERY -= battery_cost
    distance += flight_distance

    message = (
        f"You flew from "
        f"{current_airport[0]} "
        f"to "
        f"{destination_airport[0]}.\n"
        f"Destination: "
        f"{destination_airport[1]}\n"
        f"Distance: "
        f"{flight_distance:.0f} km\n"
        f"Battery used: "
        f"{battery_cost}%\n"
        f"Battery remaining: "
        f"{BATTERY}%"
    )

    return destination_airport, message


# Show help
def show_help():
    print()
    print("Commands:")
    print()
    print("fly {airport}")
    print("    Fly to an airport.")
    print()
    print("status")
    print("    Show your current status.")
    print()
    print("map")
    print("    Show nearby airports.")
    print()
    print("help")
    print("    Show this help.")
    print()
    print("exit")
    print("    Quit the game.")
    print()
    print("Examples:")
    print("    fly ARN")
    print("    fly Stockholm")
    print("    fly Stockholm Arlanda")
    print()


# Start the game
current_airport = escape_db.get_airport(START_AIRPORT)

# Check starting airport
if current_airport is None:
    print("ERROR:")
    print(f"Starting airport {START_AIRPORT} could not be found.")
    print()
    print("Check that the airport table contains the correct data.")
    input("Press Enter to exit...")
    exit()


# Start menu
clear()
prompt()
message = ""


# Gameplay loop
while True:
    clear()

    # Display player information
    print("========================================")
    print("       ICAO AIRPORT ADVENTURE")
    print("========================================")
    print()

    show_airport(current_airport)

    # Display message
    if message != "":
        print(message)
        print()

    # Check if player reached the goal
    if current_airport[0].upper() == GOAL_AIRPORT:
        print("========================================")
        print("          CONGRATULATIONS!")
        print("========================================")
        print()
        print("You reached London Heathrow.")
        print()
        print(f"Total distance: {distance:.0f} km")
        print(f"Battery remaining: {BATTERY}%")
        print()
        print("You completed your journey!")

        break

    # Check if battery is empty
    if BATTERY <= 0:
        print("Your aircraft has run out of battery.")
        print()
        print("GAME OVER")

        break

    # Show nearby airports
    show_map(current_airport)

    # Get player's command
    user_input = input("Enter your command: ").strip()

    if user_input == "":
        message = "Please enter a command."
        continue

    # Split command into words
    parts = user_input.split()

    # First word is the action
    action = parts[0].lower()

    # Fly command
    if action == "fly":

        if len(parts) < 2:
            message = "Please enter an airport.\nExample: fly ARN"

        else:
            # Everything after fly is the destination
            destination = " ".join(parts[1:])

            current_airport, message = fly(
                destination,
                current_airport
            )

    # Status command
    elif action == "status":

        show_status(current_airport)

        input("Press Enter to continue...")

        message = ""

    # Map command
    elif action == "map":

        show_map(current_airport)

        input("Press Enter to continue...")

        message = ""

    # Help command
    elif action == "help":

        show_help()

        input("Press Enter to continue...")

        message = ""

    # Exit command
    elif action == "exit":

        print()
        print("Thanks for playing!")

        break

    # Any other commands are invalid
    else:
        message = (
            "Invalid command.\n"
            "Type 'help' to see the available commands."
        )

