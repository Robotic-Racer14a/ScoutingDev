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
        
        new_scout_data[key] = (a_lev_1, a_lev_2, a_lev_3, dc_lev_1, dc_lev_2, dc_lev_3)
        
    for key, values in pit_data.items():
        new_scout_data[key] = (values[0], values[1], values[2], values[0], values[1], values[2])
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
captain = "frc2337"
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
for team in teams:
    
    
    compiled_score.append({
        "Team": team,
        "Pick Two Score": full_alliance_score,
        "Pick One Score": pick_one_score
    })

opr.print_results(compiled_score, "Pick One Score", 70, 1, True)