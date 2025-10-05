## MATRIX CALCULATIONS ##
import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpBinary
import sqlite3
import math
import random
import os

def assignments(script_name, player_list):

    # Connect to db
    try:
        db_path = os.path.join(os.path.dirname(__file__), 'clocktower.db')
        con = sqlite3.connect(db_path)
        cur = con.cursor() 
    except Exception as e:
        print(f'An error occurred: {e}.')
        exit()

    query = """
    SELECT *
    FROM players
    WHERE name IN ({})
    """.format(','.join(['?'] * len(player_list)))

    cur.execute(query, tuple(player_list))
    rows = cur.fetchall() 

    # Convert output into lists
    a, b, c, d = zip(*rows)
    player_ids = list(a)
    player_names = list(b)
    players_elo_good = list(c)
    players_elo_evil = list(d)


    # Create dataframe to store info
    players = pd.DataFrame({
        'player_id': player_ids,
        'name': player_names,
        'elo_good': players_elo_good,
        'elo_evil': players_elo_evil
    })



    # Get players recent team history
    recent_history = {}
    for player in player_ids:
        query = """
        SELECT player_id, team 
        FROM assignments
        WHERE player_id = ?
        ORDER BY assignment_id DESC
        LIMIT 10;
        """
        cur.execute(query, (player,))
        rows = cur.fetchall()
        a, b = zip(*rows)
        team_for_player = list(b)

        recent_history[player] = team_for_player



    sql = """
    SELECT character_id, name, alignment, role_type, base_strength
    FROM characters RIGHT JOIN script_characters USING (character_id)
    WHERE script_id = (
    SELECT script_id
    FROM scripts
    WHERE scripts.name = ?);
    """
    cur.execute(sql, (script_name,))
    rows = cur.fetchall()

    a, b, c, d, e = zip(*rows)
    char_ids = list(a)
    char_names = list(b)
    char_alignments = list(c)
    char_types = list(d)
    char_strengths = list(e)


    # Set up characters dataframe
    characters = pd.DataFrame({
        'character_id': char_ids,
        'name': char_names,
        'alignment': char_alignments,
        'base_strength': char_strengths,
        'role_type': char_types
        
    })

    query = """
    SELECT player_id, character_id, team, won
    FROM assignments
    WHERE player_id IN ({})
    AND character_id IN ({})""".format(','.join(['?'] * len(player_ids)),
                                       ','.join(['?'] * len(char_ids)))
    cur.execute(query, tuple(player_ids + char_ids))
    rows = cur.fetchall()

    a, b, c, d = zip(*rows)
    player_ids_assign = list(a)
    char_ids_assign = list(b)
    team_assign = list(c)
    won_assign = list(d)


    query = """
    SELECT *
    FROM type_distribution
    WHERE num_players = ?;
    """
    num_players = len(player_list)
    cur.execute(query, (num_players,))
    num_types = cur.fetchall()
    con.close()
  

    # Set up previous game data outcomes
    game_data = pd.DataFrame({
        'player_id': player_ids_assign,
        'character_id': char_ids_assign,
        'alignment': team_assign,
        'won': won_assign
    })


    ## Normalise elo to be centred around 1500
    def normaliseElo(elo):
        return (elo - 1500) / 400 

    ## Normalise base strenght to be centred around 50
    def normaliseBaseStrength(base_strength):
        return (base_strength - 50) / 25

    ## Get a players normalised elo for their alignment
    def getNormalisedElo(row):
        player = players.loc[players['player_id'] == row['player_id']].iloc[0]
        if row['alignment'] == 'Good':
            return normaliseElo(player['elo_good'])
        else:
            return normaliseElo(player['elo_evil'])


    game_data['normalized_elo'] = game_data.apply(getNormalisedElo, axis=1)

    ## Get a characters normalised strength from their id
    def getNormalisedStrength(cid):
        strength = characters.loc[characters['character_id'] == cid, 'base_strength'].values[0]
        return normaliseBaseStrength(strength)

    game_data['normalized_strength'] = game_data['character_id'].map(getNormalisedStrength)


    ## Building Bayesian logicistic model
    with pm.Model() as model:
        weighted_elo = pm.Normal('weighted_elo', mu=1, sigma=3)
        weighted_strength = pm.Normal('weighted_strength', mu=1, sigma=3)
        intercept = pm.Normal('intercept', mu=0, sigma=1)

        theta = pm.Data('theta', game_data['normalized_elo'].values)
        phi = pm.Data('phi', game_data['normalized_strength'].values)

        logits = (weighted_elo * theta) + (weighted_strength * phi) + intercept
        p = pm.Deterministic('p', pm.math.sigmoid(logits))

        outcome = pm.Bernoulli('outcome', p=p, observed=game_data['won'].values)
        map_estimate = pm.find_MAP()

    weighted_elo = map_estimate['weighted_elo']
    weighted_strength = map_estimate['weighted_strength']
    intercept = map_estimate['intercept']



   ### Generate win probability matrix S[i][j] ###
    ## Sigmoid function
    def sigmoid(x, steepness=1.5, midpoint=3):
        return 1 / (1 + np.exp(steepness * (x - midpoint)))

    ## If a player has been good more often, add bias towards being evil and vice versa
    def get_alignment_bias(player_id, target_alignment):
        history = recent_history.get(player_id, [])
        bias = 0

        if target_alignment == 'Good':
            recent_evil = history[:2].count('Evil')
            consecutive_evil = 0
            for align in history:
                if align == 'Evil':
                    consecutive_evil += 1
                else:
                    break

            base = 0.5 + 0.3 * recent_evil + 0.2 * consecutive_evil
            noise = random.uniform(-1.5, 1.5)
            bias = base + noise

        elif target_alignment == 'Evil':
            good_streak = 0
            for align in history:
                if align == 'Good':
                    good_streak += 1
                else:
                    break

            # Logistic decay
            decay = 1 / (1 + math.exp(1.2 * (good_streak - 3)))
            noise = random.uniform(0.3, 1.0)
            base = 0.3 + decay * noise

            # Add in a random element to ensure that the assignments are not predictable
            bias = base + random.uniform(0.05, 0.2)

        return round(bias, 3)


    num_players = len(players)
    num_characters = len(characters)
    S = np.zeros((num_players, num_characters))
    B = np.zeros((num_players, num_characters))

    for i, player in players.iterrows():
        for j, character in characters.iterrows():
            if character['alignment'] == 'Good':
                elo = player['elo_good']
            else:
                elo = player['elo_evil']

            norm_elo = normaliseElo(elo)
            norm_strength = normaliseBaseStrength(character['base_strength'])

            logit = weighted_elo * norm_elo + weighted_strength * norm_strength + intercept
            win_prob = 1 / (1 + np.exp(-logit))
            S[i][j] = win_prob

            bias = get_alignment_bias(player['player_id'], character['alignment'])
            B[i][j] = bias



    ## Creating an LP problem to assign characters to players to ensure the win probability for each team is as even as possible
    prob = LpProblem("CharacterAssignment", LpMinimize)
    x = [[LpVariable(f"x_{i}_{j}", cat=LpBinary) for j in range(num_characters)] for i in range(num_players)]

    ## CONSTRAINT: every player can get at most one character ##
    for i in range(num_players):
        prob += lpSum(x[i][j] for j in range(num_characters)) == 1

    ## CONSTRAINT: each character is assigned to at most one player
    for j in range(num_characters):
        prob += lpSum(x[i][j] for i in range(num_players)) <= 1



    ## CONSTRAINT: the number of each roles assigned must match the given requirements for the script
    player_requirements = {
        'Townsfolk': num_types[0][1],
        'Outsider': num_types[0][2],
        'Minion': num_types[0][3],
        'Demon': num_types[0][4]
    }
    for role_type, required_count in player_requirements.items():
        role_mask = [1 if characters.loc[j, 'role_type'] == role_type else 0 for j in range(num_characters)]
        num_align = lpSum(x[i][j] * role_mask[j] for i in range(num_players) for j in range(num_characters))
        prob += num_align == required_count

    role_usage_caps = {}
    for role_type, required_count in player_requirements.items():
        available = sum(1 for j in range(num_characters) if characters.loc[j, 'role_type'] == role_type)
        temp = int(np.ceil(required_count / available)) if available > 0 else required_count
        role_usage_caps[role_type] = temp

    for j in range(num_characters):
        role = characters.loc[j, 'role_type']
        usage_cap = role_usage_caps.get(role, 1)
        prob += lpSum(x[i][j] for i in range(num_players)) <= usage_cap



    ## CONSTRAINT: teams must be as balanced as possible
    delta = LpVariable("team_balance_gap", lowBound=0)
    team_sign = [1 if characters.loc[j, 'alignment'] == 'Good' else -1 for j in range(num_characters)]

    good_total = lpSum(x[i][j] * S[i][j] for i in range(num_players) for j in range(num_characters) if team_sign[j] == 1)
    evil_total = lpSum(x[i][j] * S[i][j] for i in range(num_players) for j in range(num_characters) if team_sign[j] == -1)

    num_good = sum(1 for j in range(num_characters) if team_sign[j] == 1)
    num_evil = sum(1 for j in range(num_characters) if team_sign[j] == -1)

    av_good = good_total / num_good
    av_evil = evil_total / num_evil



    ## OBJECTIVE: minimise the imbalance between teams and maximise bias satisfaction
    bias_score = lpSum(x[i][j] * B[i][j] for i in range(num_players) for j in range(num_characters))
    prob += delta - bias_score


    # Solve the problem
    prob.solve()

    assignments = []
    for i in range(num_players):
        for j in range(num_characters):
            if x[i][j].value() == 1:
                assignments.append({
                    'player': players.loc[i, 'name'],
                    'character': characters.loc[j, 'name'],
                    'win_probability': S[i][j],
                    'team': characters.loc[j, 'alignment']
                })

    # Output the final assignment results
    assignment_df = pd.DataFrame(assignments)
    print("\nFinal Assignments:")
    print(assignment_df)

 ## Sample example   
# script = "Sects_and_violets"
# players = ["Liza","Madi", "Rita", "Pedro", "Jed", "Oli", "Rowan"]
# assignments(script, players)
