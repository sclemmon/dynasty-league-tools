import requests
import json
from typing import Dict, Any
from datetime import datetime
import pytz

LEAGUE_ID = "1048178156026433536"
BASE_URL = "https://api.sleeper.app/v1"
PACIFIC_TIMEZONE = pytz.timezone('America/Los_Angeles')

def fetch_sleeper_data(league_id: str) -> Dict[str, Any]:
    endpoints = {
        "league": f"{BASE_URL}/league/{league_id}",
        "users": f"{BASE_URL}/league/{league_id}/users",
        "rosters": f"{BASE_URL}/league/{league_id}/rosters",
        "drafts": f"{BASE_URL}/league/{league_id}/drafts"
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

        bench_players = []
        starters_list = roster.get('starters', [])
        players_list = roster.get('players', [])
        taxi_list = roster.get('taxi', [])

        for player_id in players_list:
            if (starters_list is None or player_id not in starters_list) and \
               (reserve_list is None or player_id not in reserve_list) and \
               (taxi_list is None or player_id not in taxi_list):
                player_info = players_data.get(player_id, {})
                bench_players.append({
                    "player_id": player_id,
                    "full_name": player_info.get('full_name', 'Unknown')
                })

        organized_data[team_name] = {
            "owner_id": user_id,
            "roster_id": roster['roster_id'],
            "players": [{
                "player_id": player_id,
                "full_name": players_data.get(player_id, {}).get('full_name', 'Unknown')
            } for player_id in players_list],
            "starters": [{
                "player_id": player_id,
                "full_name": players_data.get(player_id, {}).get('full_name', 'Unknown')
            } for player_id in starters_list or []],
            "reserve": reserve_players,
            "bench": bench_players,
            "bench_count": len(bench_players),
            "taxi": [{
                "player_id": player_id,
                "full_name": players_data.get(player_id, {}).get('full_name', 'Unknown')
            } for player_id in taxi_list or []]
        }

    return organized_data

def fetch_and_organize_draft_data(league_id: str) -> Dict[str, Any]:
    drafts_url = f"{BASE_URL}/league/{league_id}/drafts"
    response = requests.get(drafts_url)
    response.raise_for_status()
    drafts_data = response.json()

    draft_details = []
    for draft in drafts_data:
        draft_id = draft['draft_id']
        draft_date = draft.get('start_time', 'Unknown')
        if draft_date != 'Unknown':
            draft_date = datetime.utcfromtimestamp(draft_date / 1000).replace(tzinfo=pytz.utc).astimezone(PACIFIC_TIMEZONE).strftime('%Y-%m-%d %H:%M:%S %Z')
        picks_url = f"{BASE_URL}/draft/{draft_id}/picks"
        response = requests.get(picks_url)
        response.raise_for_status()
        picks_data = response.json()
        draft_details.append({
            "draft_id": draft_id,
            "draft_date": draft_date,
            "draft_data": picks_data
        })

    return draft_details

def main():
    try:
        print("Fetching league data...")
        data = fetch_sleeper_data(LEAGUE_ID)

        print("Organizing data...")
        organized_rosters = organize_rosters_by_team(data)

        print("Fetching and organizing draft data...")
        draft_data = fetch_and_organize_draft_data(LEAGUE_ID)

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

            print(f"  Bench: {team_data['bench_count']}")
            for player in team_data['bench']:
                print(f"    - {player['full_name']} (ID: {player['player_id']})")

            print(f"  Taxi: {len(team_data['taxi'])}")
            for player in team_data['taxi']:
                print(f"    - {player['full_name']} (ID: {player['player_id']})")
            print()

        print("Draft Data:")
        for draft in draft_data:
            print(f"Draft ID: {draft['draft_id']}, Draft Date: {draft['draft_date']}")
            for pick in draft['draft_data']:
                print(f"  Round {pick['round']}, Pick {pick['pick_no']}: Player ID {pick['player_id']}")

        # Save the data to a JSON file
        with open(f"sleeper_league_data.json", "w") as f:
            json.dump({
                "rosters": organized_rosters,
                "drafts": draft_data
            }, f, indent=2)
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
