import json


def check_reserve_eligibility(data):
    eligible_statuses = ["Out", "PUP", "IR"]
    ineligible_teams = {}

    for team_name, team_data in data.items():
        ineligible_players = []
        for player in team_data.get("reserve", []):
            is_eligible = player.get("injury_status") in eligible_statuses
            player["is_eligible_for_reserve"] = is_eligible
            if not is_eligible:
                ineligible_players.append(player["full_name"])

        if ineligible_players:
            ineligible_teams[team_name] = ineligible_players

    return ineligible_teams


# Load the JSON data
with open('sleeper_league_1048178156026433536_data.json', 'r') as file:
    league_data = json.load(file)

# Check for ineligible players and update JSON
ineligible_teams = check_reserve_eligibility(league_data)

# Save the updated JSON data
with open('sleeper_league_1048178156026433536_data_updated.json', 'w') as file:
    json.dump(league_data, file, indent=2)

# Report the results
if ineligible_teams:
    print("Teams with ineligible players in reserve slots:")
    for team, players in ineligible_teams.items():
        print(f"{team}: {', '.join(players)}")
else:
    print("All teams have eligible players in their reserve slots.")

print("\nUpdated JSON file has been saved as 'sleeper_league_1048178156026433536_data_updated.json'")
