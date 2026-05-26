import frcOPRMethods as opr

def get_branch_scores(matches):
    new_match_list = []
    for match in matches:
        new_match_list.append({
            "red_teams": match["red_teams"],
            "red_score": match["red_score"]["tba_botRowCount"] + match["red_score"]["tba_midRowCount"] + match["red_score"]["tba_topRowCount"],
            "blue_teams": match["blue_teams"],
            "blue_score": match["blue_score"]["tba_botRowCount"] + match["blue_score"]["tba_midRowCount"] + match["blue_score"]["tba_topRowCount"],
            "match_key": match["match_key"]
            })
    return new_match_list

def get_trough_scores(matches):
    new_match_list = []
    for match in matches:
        new_match_list.append({
            "red_teams": match["red_teams"],
            "red_score": match["red_score"]["trough"],
            "blue_teams": match["blue_teams"],
            "blue_score": match["blue_score"]["trough"],
            "match_key": match["match_key"]
            })
    return new_match_list



# --- Example Usage ---

opr.event_key = "2025mil"
scouting_trust = 5 # How much to trust our data vs calculated OPR

# opr.print_match_options()
alliance_scores = opr.get_event_matches_alliance_scores(["netAlgaeCount", "autoReef", "teleopReef"])
team_objectives = opr.get_event_matches_team_objectives(["autoLine", "endGame"])
teams = opr.get_event_teams()

scouted = opr.get_data() # Data in form ("frc####", "qm##"): (autoBranchCount, autoTroughCount, teleopBranchCount, teleopTroughCount, netAlgaeCount)
#For pit scouting, use this example ("frc2337", 0): (3, 0, 17, 1, 0)

autoCoralCount = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["autoReef"]), teams, {key: value[0] for key, value in scouted.items()}, scouting_trust)
autoTroughCount = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["autoReef"]), teams, {key: value[1] for key, value in scouted.items()}, scouting_trust)
teleopCoralCount = opr.calculate_opr_weighted_per_match(get_trough_scores(alliance_scores["teleopReef"]), teams, {key: value[2] for key, value in scouted.items()}, scouting_trust)
teleopTroughCount = opr.calculate_opr_weighted_per_match(get_trough_scores(alliance_scores["teleopReef"]), teams, {key: value[3] for key, value in scouted.items()}, scouting_trust)
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
    
    if team == "frc1477":
        print((algae_tele * 1.3), endgame_score)
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