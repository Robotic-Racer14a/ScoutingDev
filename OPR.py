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
        can_lev_1 = pit_data[(key[0], "PIT")][0]
        can_lev_2 = pit_data[(key[0], "PIT")][1]
        can_lev_3 = pit_data[(key[0], "PIT")][2]
        can_lev_4 = pit_data[(key[0], "PIT")][3]
        can_net = pit_data[(key[0], "PIT")][4]
        
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
        if can_lev_4: 
            total_levels += 1
            highest = 4
        
        a_split_score = values[0] // total_levels
        a_runover_score = values[0] % total_levels
        
        a_lev_1 = 0 if not(can_lev_1) else a_split_score + a_runover_score if highest == 1 else 0
        a_lev_2 = 0 if not(can_lev_2) else a_split_score + a_runover_score if highest == 2 else 0
        a_lev_3 = 0 if not(can_lev_3) else a_split_score + a_runover_score if highest == 3 else 0
        a_lev_4 = 0 if not(can_lev_4) else a_split_score + a_runover_score if highest == 4 else 0
        
        dc_split_score = values[1] // total_levels
        dc_runover_score = values[1] % total_levels
        
        dc_lev_1 = 0 if not(can_lev_1) else dc_split_score + dc_runover_score if highest == 1 else 0
        dc_lev_2 = 0 if not(can_lev_2) else dc_split_score + dc_runover_score if highest == 2 else 0
        dc_lev_3 = 0 if not(can_lev_3) else dc_split_score + dc_runover_score if highest == 3 else 0
        dc_lev_4 = 0 if not(can_lev_4) else dc_split_score + dc_runover_score if highest == 4 else 0
        
        new_scout_data[key] = (a_lev_1, a_lev_2, a_lev_3, a_lev_4, dc_lev_1, dc_lev_2, dc_lev_3, dc_lev_4, values[2])
        
    for key, values in pit_data.items():
        new_scout_data[key] = (values[0], values[1], values[2], values[3], values[0], values[1], values[2], values[3], values[4])
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

        if lev_4_score < 0.5:
            output.append(False)
        else:
            output.append(True)

        if net_score < 0.5:
            output.append(False)
        else:
            output.append(True)
            
        new_list[(team, "PIT")] = output
        
    return new_list

# --- Example Usage ---

opr.event_key = "2025mil"
scouting_trust = 5 # How much to trust our data vs calculated OPR
captain = "frc2337"
pick_one = "frc4122"

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

a_lev_1_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["autoReef"])["Level 1"], teams, {key: value[0] for key, value in scouted.items()}, scouting_trust)
a_lev_2_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["autoReef"])["Level 2"], teams, {key: value[1] for key, value in scouted.items()}, scouting_trust)
a_lev_3_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["autoReef"])["Level 3"], teams, {key: value[2] for key, value in scouted.items()}, scouting_trust)
a_lev_4_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["autoReef"])["Level 4"], teams, {key: value[3] for key, value in scouted.items()}, scouting_trust)
dc_lev_1_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 1"], teams, {key: value[4] for key, value in scouted.items()}, scouting_trust)
dc_lev_2_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 2"], teams, {key: value[5] for key, value in scouted.items()}, scouting_trust)
dc_lev_3_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 3"], teams, {key: value[6] for key, value in scouted.items()}, scouting_trust)
dc_lev_4_scores = opr.calculate_opr_weighted_per_match(get_branch_scores(alliance_scores["teleopReef"])["Level 4"], teams, {key: value[7] for key, value in scouted.items()}, scouting_trust)
netAlgaeCount = opr.calculate_opr_weighted_per_match(alliance_scores["netAlgaeCount"], teams, {key: value[8] for key, value in scouted.items()}, scouting_trust)

autoLine = opr.calculate_team_average(team_objectives["autoLine"], teams, {"Yes": 3, "No": 0})
endGame = opr.calculate_team_average(team_objectives["endGame"], teams, {"DeepCage": 12, "ShallowCage": 6, "Parked": 2, "None": 0})

compiled_score = []
captain_a_coral = [a_lev_1_scores[captain], a_lev_2_scores[captain], a_lev_3_scores[captain], a_lev_4_scores[captain]]
pick_one_a_coral = [a_lev_1_scores[pick_one], a_lev_2_scores[pick_one], a_lev_3_scores[pick_one], a_lev_4_scores[pick_one]]

captain_dc_coral = [dc_lev_1_scores[captain], dc_lev_2_scores[captain], dc_lev_3_scores[captain], dc_lev_4_scores[captain]]
pick_one_dc_coral = [dc_lev_1_scores[pick_one], dc_lev_2_scores[pick_one], dc_lev_3_scores[pick_one], dc_lev_4_scores[pick_one]]

captain_net = (netAlgaeCount[captain])
pick_one_net = (netAlgaeCount[pick_one])

captain_objective = autoLine[captain] + endGame[captain]
pick_one_objective = autoLine[pick_one] + endGame[pick_one]

for team in teams:
    
    a_coral_score = (a_lev_1_scores[team] * 3) + (a_lev_2_scores[team] * 4) + (a_lev_3_scores[team] * 5) + (a_lev_4_scores[team] * 6)
    dc_coral_score = (dc_lev_1_scores[team] * 2) + (dc_lev_2_scores[team] * 3) + (dc_lev_3_scores[team] * 4) + (dc_lev_4_scores[team] * 5)
    net_score = (netAlgaeCount[team] * 4)
    
    objective = autoLine[team] + endGame[team]
    
    
    alliance_score = 0
    
    pick_two_a_coral = [a_lev_1_scores[team], a_lev_2_scores[team], a_lev_3_scores[team], a_lev_4_scores[team]]
    pick_two_dc_coral = [dc_lev_1_scores[team], dc_lev_2_scores[team], dc_lev_3_scores[team], dc_lev_4_scores[team]]
    pick_two_net = (netAlgaeCount[team])
    
    reef = [0, 0, 0, 0]
    overflow = 0
    for j in range(4):
        i = 3 - j
        reef[i] += captain_a_coral[i] + pick_one_a_coral[i] + pick_two_a_coral[i]
        alliance_score += (reef[i] * 1)
        
        reef[i] += captain_dc_coral[i] + pick_one_dc_coral[i] + pick_two_dc_coral[i] + overflow if i > 0 else 0
        if reef[i] > 12:
            overflow = reef[i] - 12
            reef[i] = 12
        alliance_score += (reef[i] * (2 + i))
        
        reef[i] = round(float(reef[i]), 1)
        pick_two_dc_coral[i] = round(float(pick_two_dc_coral[i]), 1)
        
    alliance_score += (captain_net + pick_one_net + pick_two_net) * 4
    alliance_score += objective
    
    compiled_score.append({
        "Team": team,
        "Pick Two Score": alliance_score,
        "Net Count": pick_two_net,
        "Total Score": a_coral_score + dc_coral_score + net_score + objective
    })

opr.print_results(compiled_score, "Pick Two Score", 70, 1, True)