import frcOPRMethods as opr

def get_grid_scores(matches):
    lev_1_list = []
    lev_2_list = []
    lev_3_list = []
    for match in matches:
        lev_1_list.append({
            "red_teams": match["red_teams"],
            "red_score": 9 - match["red_score"]["B"].count("None"),
            "blue_teams": match["blue_teams"],
            "blue_score": 9 - match["blue_score"]["B"].count("None"),
            "match_key": match["match_key"]
            })
        lev_2_list.append({
            "red_teams": match["red_teams"],
            "red_score": 9 - match["red_score"]["M"].count("None"),
            "blue_teams": match["blue_teams"],
            "blue_score": 9 - match["blue_score"]["M"].count("None"),
            "match_key": match["match_key"]
            })
        lev_3_list.append({
            "red_teams": match["red_teams"],
            "red_score": 9 - match["red_score"]["T"].count("None"),
            "blue_teams": match["blue_teams"],
            "blue_score": 9 - match["blue_score"]["T"].count("None"),
            "match_key": match["match_key"]
            })
    return {
            "Level 1": lev_1_list,
            "Level 2": lev_2_list,
            "Level 3": lev_3_list,
            }


def combine_match_and_pit(match_data, pit_data):
    
    new_scout_data = {}
    for key, values in match_data.items():
        can_lev_1 = pit_data[(key[0], "PIT")][0]
        can_lev_2 = pit_data[(key[0], "PIT")][1]
        can_lev_3 = pit_data[(key[0], "PIT")][2]
        
        total_levels = 0
        if can_lev_1: 
            total_levels += 1
            highest = 1
        if can_lev_2: 
            total_levels += 1
            highest = 2
        if can_lev_3: 
            total_levels += 1
            highest = 3
        
        a_split_score = values[0] // total_levels
        a_runover_score = values[0] % total_levels
        
        a_lev_1 = 0 if not(can_lev_1) else a_split_score + a_runover_score if highest == 1 else 0
        a_lev_2 = 0 if not(can_lev_2) else a_split_score + a_runover_score if highest == 2 else 0
        a_lev_3 = 0 if not(can_lev_3) else a_split_score + a_runover_score if highest == 3 else 0
        
        dc_split_score = values[1] // total_levels
        dc_runover_score = values[1] % total_levels
        
        dc_lev_1 = 0 if not(can_lev_1) else dc_split_score + dc_runover_score if highest == 1 else 0
        dc_lev_2 = 0 if not(can_lev_2) else dc_split_score + dc_runover_score if highest == 2 else 0
        dc_lev_3 = 0 if not(can_lev_3) else dc_split_score + dc_runover_score if highest == 3 else 0
        
        new_scout_data[key] = (a_lev_1, a_lev_2, a_lev_3, dc_lev_1, dc_lev_2, dc_lev_3, highest)
        
    for key, values in pit_data.items():
        highest = 3 if values[2] else 2 if values[1] else 1
        new_scout_data[key] = (values[0], values[1], values[2], values[0], values[1], values[2], highest)
    return new_scout_data

def estimate_pit_data(lev_1, lev_2, lev_3, pit_data):
    new_list = {}
    for team, lev_1_score in lev_1.items():
        if (team, "PIT") in pit_data:
            new_list[(team, "PIT")] = pit_data[(team, "PIT")]
            continue
        
        lev_2_score = lev_2[team]
        lev_3_score = lev_3[team]
        output = []
        
        if lev_1_score < 0.5:
            output.append(False)
        else:
            output.append(True)
        
        if lev_2_score < 0.5:
            output.append(False)
        else:
            output.append(True)

        if lev_3_score < 0.5:
            output.append(False)
        else:
            output.append(True)
            
        new_list[(team, "PIT")] = output
        
    return new_list

# --- Example Usage ---

opr.event_key = "2023micmp3"
scouting_trust = 5 # How much to trust our data vs calculated OPR
captain = ""
pick_one = ""

# opr.print_match_options()
alliance_scores = opr.get_event_matches_alliance_scores(["autoCommunity", "teleopCommunity"])
team_objectives = opr.get_event_matches_team_objectives(["mobility", "autoChargeStation", "endGameChargeStation"])
teams = opr.get_event_teams()

match_scouted = opr.get_match_data()
pit_scouted = estimate_pit_data(
    opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["teleopCommunity"])["Level 1"], teams),
    opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["teleopCommunity"])["Level 2"], teams),
    opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["teleopCommunity"])["Level 3"], teams),
    opr.get_pit_data()
    )
scouted = combine_match_and_pit(match_scouted, pit_scouted)
team_highest = {key[0]: value[6] for key, value in scouted.items()}

a_lev_1_scores = opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["autoCommunity"])["Level 1"], teams, {key: value[0] for key, value in scouted.items()}, scouting_trust)
a_lev_2_scores = opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["autoCommunity"])["Level 2"], teams, {key: value[1] for key, value in scouted.items()}, scouting_trust)
a_lev_3_scores = opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["autoCommunity"])["Level 3"], teams, {key: value[2] for key, value in scouted.items()}, scouting_trust)
dc_lev_1_scores = opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["teleopCommunity"])["Level 1"], teams, {key: value[3] for key, value in scouted.items()}, scouting_trust)
dc_lev_2_scores = opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["teleopCommunity"])["Level 2"], teams, {key: value[4] for key, value in scouted.items()}, scouting_trust)
dc_lev_3_scores = opr.calculate_opr_weighted_per_match(get_grid_scores(alliance_scores["teleopCommunity"])["Level 3"], teams, {key: value[5] for key, value in scouted.items()}, scouting_trust)

autoLine = opr.calculate_team_average(team_objectives["mobility"], teams, {"Yes": 3, "No": 0})
autoBalance = opr.calculate_team_average(team_objectives["autoChargeStation"], teams, {"Docked": 12, "None": 0})
endGame = opr.calculate_team_average(team_objectives["endGameChargeStation"], teams, {"Docked": 10, "Park": 3, "None": 0})

compiled_score = []
if (not captain == ""):
    captain_a_grid = [a_lev_1_scores[captain], a_lev_2_scores[captain], a_lev_3_scores[captain]]
    captain_dc_scores = dc_lev_1_scores[captain] + dc_lev_2_scores[captain] + dc_lev_3_scores[captain]
    captain_highest = team_highest[captain]
else:
    captain_a_grid = [0, 0, 0]
    captain_dc_scores = 0
    captain_highest = 0

if (not pick_one == ""):
    captain_a_grid += [a_lev_1_scores[pick_one], a_lev_2_scores[pick_one], a_lev_3_scores[pick_one]]
    captain_dc_scores += dc_lev_1_scores[pick_one] + dc_lev_2_scores[pick_one] + dc_lev_3_scores[pick_one]
for team in teams:
    
    # Figure Out Pick One
    
    team_a_grid = [a_lev_1_scores[team], a_lev_2_scores[team], a_lev_3_scores[team]]
    team_dc_scores = dc_lev_1_scores[team] + dc_lev_2_scores[team] + dc_lev_3_scores[team]
    team_highest_score = team_highest[team]
    
    captain_temp = captain_dc_scores
    alliance_combined = captain_temp + team_dc_scores
    
    compiled_grid = [0, 0, 0]
    pick_score = 0
    for i in range(3):
        #Flip to loop top to bottom
        j = 2 - i
        
        compiled_grid[j] = team_a_grid[j] + captain_a_grid[j]
        pick_score += compiled_grid[j]
        
        spots_left = 9 - compiled_grid[j]
        
        if (captain_highest >= (j + 1) and team_highest_score >= (j + 1)):
            if (alliance_combined > spots_left):
                compiled_grid[j] = 9
                alliance_combined -= spots_left
            else:
                compiled_grid[j] += alliance_combined
                alliance_combined = 0
        elif (captain_highest >= (j + 1) and not team_highest_score >= (j + 1)):
            if (captain_temp > spots_left):
                compiled_grid[j] = 9
                alliance_combined -= spots_left
                captain_temp -= spots_left
            else:
                compiled_grid[j] += captain_temp
                alliance_combined -= captain_temp
                captain_temp = 0
        elif (not captain_highest >= (j + 1) and team_highest_score >= (j + 1)):
            if (team_dc_scores > spots_left):
                compiled_grid[j] = 9
                alliance_combined -= spots_left
                team_dc_scores -= spots_left
            else:
                compiled_grid[j] += team_dc_scores
                alliance_combined -= team_dc_scores
                team_dc_scores = 0
                
        compiled_grid[j] = round(compiled_grid[j])
        pick_score += (compiled_grid[j] * (3 + j)) + ((compiled_grid[j] // 3) * 5)
    
    compiled_grid.append(round(alliance_combined))
    pick_score += (alliance_combined * 3)
        
    print(f"{team} - {compiled_grid}")
    
    # Figure Out Pick Two
    
    compiled_score.append({
        "Team": team,
        "Pick Score": pick_score
    })

opr.print_results(compiled_score, "Pick Score", 70, 1, True)