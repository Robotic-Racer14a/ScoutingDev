import frcOPRMethods as opr

def get_branch_scores(matches):
    new_match_list = {}
    lev_1_list = []
    lev_2_list = []
    lev_3_list = []
    lev_4_list = []
    for match in matches:
        lev_1_list.append({
            "red_teams": match["red_teams"],
            "red_score": match["red_score"]["trough"],
            "blue_teams": match["blue_teams"],
            "blue_score": match["blue_score"]["trough"],
            "match_key": match["match_key"]
            })
        lev_2_list.append({
            "red_teams": match["red_teams"],
            "red_score": match["red_score"]["tba_botRowCount"],
            "blue_teams": match["blue_teams"],
            "blue_score": match["blue_score"]["tba_botRowCount"],
            "match_key": match["match_key"]
            })
        lev_3_list.append({
            "red_teams": match["red_teams"],
            "red_score": match["red_score"]["tba_midRowCount"],
            "blue_teams": match["blue_teams"],
            "blue_score":match["blue_score"]["tba_midRowCount"],
            "match_key": match["match_key"]
            })
        lev_4_list.append({
            "red_teams": match["red_teams"],
            "red_score": match["red_score"]["tba_topRowCount"],
            "blue_teams": match["blue_teams"],
            "blue_score": match["blue_score"]["tba_topRowCount"],
            "match_key": match["match_key"]
            })
    return {
            "Level 1": lev_1_list,
            "Level 2": lev_2_list,
            "Level 3": lev_3_list,
            "Level 4": lev_4_list,
            }


def combine_match_and_pit(match_data, pit_data):
    
    new_scout_data = {}
    for key, values in match_data.items():
        new_scout_data[key] = values
        
    for key, values in pit_data.items():
        new_scout_data[key] = values
    return new_scout_data

def estimate_pit_data(lev_1, lev_2, lev_3, lev_4, net, pit_data):
    new_list = {}
    for team, lev_1_score in lev_1.items():
        if (team, "PIT") in pit_data:
            new_list[(team, "PIT")] = pit_data[(team, "PIT")]
            continue
        
        lev_2_score = lev_2[team]
        lev_3_score = lev_3[team]
        lev_4_score = lev_4[team]
        net_score = net[team]
        output = []
        
        if lev_1_score < 0.5:
            output.append("No")
        else:
            output.append("Yes")
        
        if lev_2_score < 0.5:
            output.append("No")
        else:
            output.append("Yes")

        if lev_3_score < 0.5:
            output.append("No")
        else:
            output.append("Yes")

        if lev_4_score < 0.5:
            output.append("No")
        else:
            output.append("Yes")

        if net_score < 0.5:
            output.append("No")
        else:
            output.append("Yes")
            
        new_list[(team, "PIT")] = output
        
    return new_list

# --- Example Usage ---

opr.event_key = "2025mil"
scouting_trust = 5 # How much to trust our data vs calculated OPR

# opr.print_match_options()
alliance_scores = opr.get_event_matches_alliance_scores(["netAlgaeCount", "autoReef", "teleopReef"])
team_objectives = opr.get_event_matches_team_objectives(["autoLine", "endGame"])
teams = opr.get_event_teams()

match_scouted = opr.get_match_data()
pit_scouted = estimate_pit_data(
    opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 1"], teams),
    opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 2"], teams),
    opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 3"], teams),
    opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 4"], teams),
    opr.calculate_opr_weighted_per_match(alliance_scores["netAlgaeCount"], teams),
    opr.get_pit_data()
    )
scouted = combine_match_and_pit(match_scouted, pit_scouted)




netAlgaeCount = opr.calculate_opr_weighted_per_match(alliance_scores["netAlgaeCount"], teams, {key: value[4] for key, value in scouted.items()}, scouting_trust)

autoLine = opr.calculate_team_average(team_objectives["autoLine"], teams, {"Yes": 3, "No": 0})
endGame = opr.calculate_team_average(team_objectives["endGame"], teams, {"DeepCage": 12, "ShallowCage": 6, "Parked": 2, "None": 0})


compiled_score = []
for team in teams:
    
    auto_trough_score = (autoTroughCount[team] * 3)
    auto_branch_score = (autoCoralCount[team] * 6)
    
    if auto_trough_score > auto_branch_score:
        auto_score = auto_trough_score + autoLine[team]
        center_auto_check = autoLine[team]
        if auto_trough_score > 3:
            center_auto_check += 3
        else:
            center_auto_check += auto_trough_score
    else:
        auto_score = auto_branch_score + autoLine[team]
        center_auto_check = autoLine[team]
        if auto_branch_score > 6:
            center_auto_check += 6
        else:
            center_auto_check += auto_branch_score
            
    branch_tele = (teleopCoralCount[team] * 5)
    algae_tele = (netAlgaeCount[team] * 4)
    trough_tele = (teleopTroughCount[team] * 2)
    endgame_score = endGame[team]
    
    compiled_score.append({
        "Team": team,
        "Algae 1st Score": auto_score + (algae_tele * 1.2) + (branch_tele * 0.7) + endgame_score + trough_tele,
        "Branch 1st Score": auto_score + (branch_tele * 1.2) + (algae_tele * 0.7) + endgame_score + trough_tele,
        "Algae 2nd Score": center_auto_check + (algae_tele * 1.3) + (branch_tele * 0.6) + endgame_score + trough_tele,
        "Branch 2nd Score": center_auto_check + (branch_tele * 1.3) + (algae_tele * 0.6) + endgame_score + trough_tele,
        "Rounded 2nd Score": center_auto_check + branch_tele + algae_tele + endgame_score + trough_tele,
        "Total Score": auto_score + algae_tele + branch_tele + endgame_score + trough_tele
    })

opr.print_results(compiled_score, "Algae 2nd Score", 50, 1, True)