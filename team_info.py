import requests
import json
import os
from typing import Dict, Any

LEAGUE_ID = "1048178156026433536"
BASE_URL = "https://api.sleeper.app/v1"

def fetch_sleeper_data(league_id: str) -> Dict[str, Any]:
    endpoints = {
        "league": f"{BASE_URL}/league/{league_id}",
        "users": f"{BASE_URL}/league/{league_id}/users",
        "rosters": f"{BASE_URL}/league/{league_id}/rosters"
    }

    data = {}
    for key, url in endpoints.items():
        response = requests.get(url)
        response.raise_for_status()
        data[key] = response.json()

    # Fetch player data
    players_url = f"{BASE_URL}/players/nfl"
    response = requests.get(players_url)
    response.raise_for_status()
    data["players"] = response.json()

    return data

def organize_rosters_by_team(data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    organized_data = {}
    user_map = {user['user_id']: user['display_name'] for user in data['users']}
    players_data = data['players']

    for roster in data['rosters']:
        user_id = roster['owner_id']
        team_name = user_map.get(user_id, "Unknown Team")

        reserve_players = []
        reserve_list = roster.get('reserve', [])
        if reserve_list is not None:
            for player_id in reserve_list:
                player_info = players_data.get(player_id, {})
                reserve_players.append({
                    "player_id": player_id,
                    "full_name": player_info.get('full_name', 'Unknown'),
                    "injury_status": player_info.get('injury_status', 'Unknown')
                })

        organized_data[team_name] = {
            "owner_id": user_id,
            "roster_id": roster['roster_id'],
            "players": roster.get('players', []),
            "starters": roster.get('starters', []),
            "reserve": reserve_players,
            "taxi": roster.get('taxi', [])
        }

    return organized_data

def main():
    try:
        print("Fetching league data...")
        data = fetch_sleeper_data(LEAGUE_ID)

        print("Organizing data...")
        print(f"Debug: Number of rosters: {len(data['rosters'])}")
        for i, roster in enumerate(data['rosters']):
            print(f"Debug: Roster {i + 1} reserve: {roster.get('reserve')}")
            print(f"Debug: Roster {i + 1} full data: {roster}")

        organized_rosters = organize_rosters_by_team(data)

        print(f"\nLeague Name: {data['league']['name']}")
        print(f"Total Teams: {len(organized_rosters)}\n")

        for team_name, team_data in organized_rosters.items():
            print(f"Team: {team_name}")
            print(f"  Owner ID: {team_data['owner_id']}")
            print(f"  Roster ID: {team_data['roster_id']}")
            print(f"  Players: {len(team_data['players'])}")
            print(f"  Starters: {len(team_data['starters'])}")

            print(f"  Reserve (IR): {len(team_data['reserve'])}")
            for player in team_data['reserve']:
                print(f"    - {player['full_name']} (Status: {player['injury_status']})")

            print(f"  Taxi: {len(team_data['taxi'])}")
            print()

        # Print the current working directory for debugging (optional)
        print(f"Current working directory: {os.getcwd()}")

        # Save the data to a JSON file
        with open(f"sleeper_league_{LEAGUE_ID}_data.json", "w") as f:
            json.dump(organized_rosters, f, indent=2)
        print(f"Data saved to sleeper_league_{LEAGUE_ID}_data.json")

    except requests.RequestException as e:
        print(f"Error fetching data from Sleeper API: {e}")
    except KeyError as e:
        print(f"Error processing data: Missing key {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON data: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
