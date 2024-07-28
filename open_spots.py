import json

# Load the JSON data from the file
with open('sleeper_league_data.json', 'r') as file:
    data = json.load(file)

def calculate_open_spots(team_data):
    starters_count = len(team_data.get('starters', []))
    bench_count = len(team_data.get('bench', []))
    taxi_count = len(team_data.get('taxi', []))
    open_spots = 30 - (starters_count + bench_count + taxi_count)
    return open_spots

# Create a dictionary to store the results
results = {}

# Iterate over each team in the JSON data
for team_name, team_data in data.items():
    open_spots = calculate_open_spots(team_data)
    results[team_name] = {
        'owner_id': team_data['owner_id'],
        'roster_id': team_data['roster_id'],
        'open_spots': open_spots
    }

# Print the results
for team_name, team_info in results.items():
    print(f"Team: {team_name}")
    print(f"  Owner ID: {team_info['owner_id']}")
    print(f"  Roster ID: {team_info['roster_id']}")
    print(f"  Open Spots: {team_info['open_spots']}")
    print()

# Optionally, save the results to a JSON file
with open('open_spots_results.json', 'w') as outfile:
    json.dump(results, outfile, indent=2)

print("Results saved to open_spots_results.json")
