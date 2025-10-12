## MATRIX CALCULATIONS ##
import numpy as np
import pandas as pd
import pymc as pm
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpBinary, value
import sqlite3
import math
import random
import db_setup
from character_constraints import character_constraints, xaan_constraint

def assignments(script_name, player_list):
    # Connect to db
    try:
        con = sqlite3.connect(db_setup.db_path)
        cur = con.cursor()
    except Exception as e:
        print(f'An error occurred: {e}.')
        return

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
        try:
            a, b = zip(*rows)
            team_for_player = list(b)
        except:
            team_for_player = ['Good', 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', 'Good', 'Good']
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
    }).sample(frac=1).reset_index(drop=True)  # shuffle to break deterministic ties

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


    # Suppose you already have your characters dataframe
    # Find the Village Idiot row
    vi_row = characters[characters['name'] == 'Village Idiot']

    # Duplicate it up to 3 times (with unique indices)
    for k in range(2, 4):  # add VI_2 and VI_3
        new_row = vi_row.copy()
        new_row['name'] = f"Village Idiot {k}"   # give them unique names
        characters = pd.concat([characters, new_row], ignore_index=True)
    # --- Normalisation helpers ---
    def normaliseElo(elo): return (elo - 1500) / 400
    def normaliseBaseStrength(bs): return (bs - 50) / 25

    def getNormalisedElo(row):
        player = players.loc[players['player_id'] == row['player_id']].iloc[0]
        return normaliseElo(player['elo_good'] if row['alignment'] == 'Good' else player['elo_evil'])

    game_data['normalized_elo'] = game_data.apply(getNormalisedElo, axis=1)

    def getNormalisedStrength(cid):
        strength = characters.loc[characters['character_id'] == cid, 'base_strength'].values[0]
        return normaliseBaseStrength(strength)

    # --- Alignment bias from history ---
    def get_alignment_bias(player_id, target_alignment):
        history = recent_history.get(player_id, [])
        if target_alignment == 'Good':
            recent_evil = history[:2].count('Evil')
            consecutive_evil = 0
            for align in history:
                if align == 'Evil': consecutive_evil += 1
                else: break
            base = 0.5 + 0.3 * recent_evil + 0.2 * consecutive_evil
            noise = random.uniform(-1.5, 1.5)
            return round(base + noise, 3)
        else:
            good_streak = 0
            for align in history:
                if align == 'Good': good_streak += 1
                else: break
            decay = 1 / (1 + math.exp(1.2 * (good_streak - 3)))
            noise = random.uniform(0.3, 1.0)
            base = 0.3 + decay * noise
            return round(base + random.uniform(0.05, 0.2), 3)

    game_data['normalized_strength'] = game_data['character_id'].map(getNormalisedStrength)

    # --- Base requirements from table ---
    player_requirements = {
        'Townsfolk': num_types[0][1],
        'Outsider':  num_types[0][2],
        'Minion':    num_types[0][3],
        'Demon':     num_types[0][4],
    }

    # --- Build model ---
    accept = False
    while not accept:
        if 'forced_evil' not in characters.columns:
            characters['forced_evil'] = False
        else:
            characters['forced_evil'] = False

        # Fit logistic model
        with pm.Model() as model:
            weighted_elo = pm.Normal('weighted_elo', mu=1, sigma=3)
            weighted_strength = pm.Normal('weighted_strength', mu=1, sigma=3)
            intercept = pm.Normal('intercept', mu=0, sigma=1)

            theta = pm.Data('theta', game_data['normalized_elo'].values)
            phi   = pm.Data('phi',   game_data['normalized_strength'].values)

            logits = (weighted_elo * theta) + (weighted_strength * phi) + intercept
            p = pm.Deterministic('p', pm.math.sigmoid(logits))
            pm.Bernoulli('outcome', p=p, observed=game_data['won'].values)

            map_estimate = pm.find_MAP()

        weighted_elo = map_estimate['weighted_elo']
        weighted_strength = map_estimate['weighted_strength']
        intercept = map_estimate['intercept']

        num_players = len(players)
        num_characters = len(characters)

        # Create problem and decision variables
        prob = LpProblem("CharacterAssignment", LpMinimize)
        x = [[LpVariable(f"x_{i}_{j}", cat=LpBinary) for j in range(num_characters)] for i in range(num_players)]

        # Each player gets exactly one character
        for i in range(num_players):
            prob += lpSum(x[i][j] for j in range(num_characters)) == 1

        # Each character to at most one player
        for j in range(num_characters):
            prob += lpSum(x[i][j] for i in range(num_players)) <= 1

        # Apply character-specific constraints and collect adjusted requirements
        adjusted_requirements = dict(player_requirements)
        hooks = []  # post-solve hooks only
        logging_results = []

        xaan_index = None
        xaan_in_play = None
        xaan_target = None



        for char_name, fn in character_constraints.items():
            if char_name in characters['name'].values:
                char_index = characters[characters['name'] == char_name].index[0]

                # Special handling for Xaan
                if char_name == "Xaan":
                    xaan_index = char_index
                    xaan_in_play = lpSum(x[i][xaan_index] for i in range(num_players))
                    xaan_target = np.random.randint(1, 5)
                    result = fn(prob, x, characters, players, player_requirements, xaan_index, xaan_target)
                else:
                    result = fn(prob, x, characters, players, player_requirements, char_index)

                # Log and collect post-solve hooks
                if "_log" in result:
                    print(f"[Constraint Applied] {result['_log']}")
                    logging_results.append({result['_log']})
                if "_hook" in result:
                    hooks.append(result["_hook"])


                # Remove helper entries before folding into adjusted_requirements
                result.pop("_log", None)
                result.pop("_hook", None)

                for role_type, delta in result.items():
                    if isinstance(role_type, str) and role_type.startswith("_"):
                        continue
                    adjusted_requirements[role_type] = adjusted_requirements.get(role_type, 0) + delta

        # Summoner role-type deltas
        if "Summoner" in characters['name'].values:
            summoner_index = characters[characters['name'] == "Summoner"].index[0]
            summoner_in_play = lpSum(x[i][summoner_index] for i in range(num_players))
            adjusted_requirements["Demon"] = player_requirements['Demon'] - summoner_in_play
            adjusted_requirements["Townsfolk"] = player_requirements['Townsfolk'] + summoner_in_play
            print("[Constraint Applied] Summoner → Demons -1, Townsfolk +1")

        # Kazali index for objective weighting
        kazali_index = characters[characters['name'] == "Kazali"].index[0] if "Kazali" in characters['name'].values else None
        # Lil' Monsta adjustments (global var created in its constraint)
        if "Lil' Monsta" in characters['name'].values:
            try:
                y_monsta = next(v for v in prob.variables() if v.name == "lilmonsta_in_play")
            except StopIteration:
                y_monsta = None
            minion_indices = characters[characters['role_type'] == 'Minion'].index.tolist()
            lilmonsta_adjustments = (y_monsta, minion_indices)
        else:
            lilmonsta_adjustments = None

        # Build S and B
        S = np.zeros((num_players, num_characters))
        B = np.zeros((num_players, num_characters))
        for i, player in players.iterrows():
            for j, character in characters.iterrows():
                elo = player['elo_good'] if character['alignment'] == 'Good' else player['elo_evil']
                norm_elo = (elo - 1500) / 400
                norm_strength = (character['base_strength'] - 50) / 25
                logit = weighted_elo * norm_elo + weighted_strength * norm_strength + intercept
                win_prob = 1 / (1 + np.exp(-logit))
                jitter = np.random.uniform(-0.02, 0.02)
                if character['role_type'] == 'Minion':
                    jitter += np.random.uniform(-0.05, 0.05)
                S[i][j] = np.clip(win_prob + jitter, 0.0, 1.0)
                B[i][j] = get_alignment_bias(player['player_id'], character['alignment'])

        # Role totals
        role_totals = {}
        for role_type in ['Townsfolk', 'Outsider', 'Minion', 'Demon']:
            role_mask = [1 if characters.loc[j, 'role_type'] == role_type else 0 for j in range(num_characters)]
            role_totals[role_type] = lpSum(x[i][j] * role_mask[j] for i in range(num_players) for j in range(num_characters))

        # Enforce adjusted role requirements (no per-character caps)
        for role_type in ['Townsfolk', 'Outsider', 'Minion', 'Demon']:
            required_count = adjusted_requirements.get(role_type, player_requirements[role_type])
            if role_type == 'Outsider' and xaan_index is not None:
                continue
            prob += role_totals[role_type] == required_count


        # Team balance with tolerance
        team_sign = [1 if characters.loc[j, 'alignment'] == 'Good' else -1 for j in range(num_characters)]
        good_total = lpSum(x[i][j] * S[i][j] for i in range(num_players) for j in range(num_characters) if team_sign[j] == 1)
        evil_total = lpSum(x[i][j] * S[i][j] for i in range(num_players) for j in range(num_characters) if team_sign[j] == -1)

        num_good_chars = sum(1 for j in range(num_characters) if team_sign[j] == 1)
        num_evil_chars = sum(1 for j in range(num_characters) if team_sign[j] == -1)

        av_good = good_total / (num_good_chars if num_good_chars > 0 else 1)
        av_evil = evil_total / (num_evil_chars if num_evil_chars > 0 else 1)

        bias_score = lpSum(x[i][j] * B[i][j] for i in range(num_players) for j in range(num_characters))

        tolerance = 1.0
        excess = LpVariable("excess_imbalance", lowBound=0)
        prob += av_good - av_evil <= tolerance + excess
        prob += av_evil - av_good <= tolerance + excess

        # Objective
        objective = excess - bias_score
        num_demons = (characters['role_type'] == 'Demon').sum()
        # Summoner objective buffer
        if "Summoner" in characters['name'].values:
            summoner_var = lpSum(x[i][summoner_index] for i in range(num_players))
            
            summoner_buffer = ((num_demons + 1) / (num_demons * 2))
            objective += summoner_buffer * summoner_var

        # Kazali objective buffer
        if kazali_index is not None:
            kazali_var = lpSum(x[i][kazali_index] for i in range(num_players))
            
            kazali_buffer = ((num_demons) / (num_demons + 2)) if num_players <= 8 else (num_players) / (num_demons * 2)
            objective += kazali_buffer * kazali_var
        

        lord_index = characters[characters['name'] == "Lord Of Typhon"].index[0] if "Lord Of Typhon" in characters['name'].values else None

        if "Lord Of Typhon" in characters['name'].values and random.random() < (1/num_demons):
            prob += lpSum(x[i][lord_index] for i in range(num_players)) == 1
        # prob += lord_of_typhon_var == 1 ### ENFORCING LORD OF TYPHON

        # Light noise
        noise = lpSum(np.random.uniform(-0.05, 0.05) * x[i][j] for i in range(num_players) for j in range(num_characters))
        objective += noise

        prob += objective

        # Reset drunk flags and solve
        players['drunk'] = False
        prob.solve()

        # Post-solve: apply Lil' Monsta boost directly to S (no hooks)
        if lilmonsta_adjustments:
            y_monsta, minion_indices = lilmonsta_adjustments
            val = value(y_monsta) if y_monsta is not None else None
            if val is not None and val > 0.5 and minion_indices:
                for j in minion_indices:
                    for i in range(num_players):
                        # Recompute S with +20 base_strength for Minions
                        elo = players.loc[i, 'elo_good'] if characters.loc[j, 'alignment'] == 'Good' else players.loc[i, 'elo_evil']
                        norm_elo = (elo - 1500) / 400
                        norm_strength = ((characters.loc[j, 'base_strength'] + 20.0) - 50) / 25
                        logit = weighted_elo * norm_elo + weighted_strength * norm_strength + intercept
                        win_prob = 1 / (1 + np.exp(-logit))
                        S[i][j] = np.clip(win_prob, 0.0, 1.0)
                print("✅ Lil' Monsta in play: all Minions boosted by +20 base_strength in S.")
            else:
                print("ℹ️ Lil' Monsta not in play (no S boost applied).")

        # Post-solve message: Lil’ Monsta babysitting (global token; not assigned to players)
        try:
            y_monsta = next(v for v in prob.variables() if v.name == "lilmonsta_in_play")
            val = value(y_monsta)
            if val is not None and val > 0.5:
                print("✅ Lil' Monsta is in play. A Minion must babysit it.")
            else:
                print("ℹ️ Lil' Monsta not in play.")
        except StopIteration:
            pass

        # Run post-solve hooks (e.g., BH target resolution)
        for hook in hooks:
            msg = hook(characters, players)
            print(f"[Post-Solve Adjustment] {msg}")


        # Diagnostics
        print("Objective components:")
        print("  Excess imbalance:", value(excess))
        print("  Bias score:", value(bias_score))
        # if "Baron" in characters['name'].values:
        #     print("  Baron chosen:", value(baron_var))



        # Build assignments
        assigned = []
        to_output = ""

        for i in range(num_players):
            for j in range(num_characters):
                if x[i][j].value() == 1:
                    team = characters.loc[j, 'alignment']

                    if 'forced_evil' in characters.columns and characters.loc[j, 'forced_evil']:
                        team = "Evil"
                        to_output = characters.loc[j, 'name'] + " is evil because of the Bounty Hunter"

                    drunk_flag = bool(players.loc[i, 'drunk'])

                    assigned.append({
                        'player': players.loc[i, 'name'],
                        'character': characters.loc[j, 'name'],
                        'role_type': characters.loc[j, 'role_type'],
                        'win_probability': float(np.clip(S[i][j], 0.0, 1.0)),
                        'team': team,
                        'drunk': "Drunk" if drunk_flag else "_"
                    })

        # import random
        # import pandas as pd

        
        def rearrange_for_lord_of_typhon(assignments_df):
            # If Lord not present, return unchanged
            if "Lord Of Typhon" not in assignments_df['character'].values:
                return assignments_df

            # Split Evil and Good
            evil_df = assignments_df[assignments_df['team'] == 'Evil'].copy()
            good_df = assignments_df[assignments_df['team'] == 'Good'].copy()

            # Identify Lord row and other evil
            lord_row = evil_df[evil_df['character'] == "Lord Of Typhon"]
            other_evil = evil_df[evil_df['character'] != "Lord Of Typhon"]

            n_minions = len(other_evil)
            block_size = n_minions + 1  # Lord + Minions

            if block_size < 3:
                raise ValueError("Lord of Typhon requires at least 2 Minions, so evil block size must be ≥ 3")

            if block_size == 3:
                # Always Lord in the middle
                evil_reordered = pd.concat([other_evil.iloc[:1], lord_row, other_evil.iloc[1:]])
            elif block_size == 4:
                # Lord can be at position 2 or 3 (1-indexed)
                if random.choice([True, False]):
                    evil_reordered = pd.concat([other_evil.iloc[:1], lord_row, other_evil.iloc[1:]])
                else:
                    evil_reordered = pd.concat([other_evil.iloc[:2], lord_row, other_evil.iloc[2:]])
            else:
                # General case: put Lord at or near the middle
                mid = block_size // 2
                if block_size % 2 == 1:
                    # Odd length: exact middle
                    evil_reordered = pd.concat([other_evil.iloc[:mid], lord_row, other_evil.iloc[mid:]])
                else:
                    # Even length: Lord can be mid or mid+1
                    if random.choice([True, False]):
                        evil_reordered = pd.concat([other_evil.iloc[:mid-1], lord_row, other_evil.iloc[mid-1:]])
                    else:
                        evil_reordered = pd.concat([other_evil.iloc[:mid], lord_row, other_evil.iloc[mid:]])

            # Random insertion point for the evil block among the good rows
            good_rows = [row.to_frame().T for _, row in good_df.iterrows()]
            insert_pos = random.randint(0, len(good_rows))
            blocks = good_rows[:insert_pos] + [evil_reordered] + good_rows[insert_pos:]

            final_df = pd.concat(blocks, ignore_index=True)
            return final_df


        df = pd.DataFrame(assigned)
        df = rearrange_for_lord_of_typhon(df)
        print("\nFinal Assignments:")
        print(df.to_string(index=False))
        print("\n========== Final Adjusted Role Requirements ==========")
        for role_type in ['Townsfolk', 'Outsider', 'Minion', 'Demon']:
            base = player_requirements.get(role_type, 0)
            adjusted = adjusted_requirements.get(role_type, base)
            print(f"{role_type}: base={base}, enforced={adjusted}")
        print("======================================================\n")
        print(logging_results)
        print(to_output)

        # accept?
        valid_accept = False
        while not valid_accept:
            accept_assign = str(input("Accept assignment? Y/N   ")).upper()
            if accept_assign == "Y":
                accept = True
                valid_accept = True
            elif accept_assign == "N":
                valid_accept = True
            else:
                print("Please enter valid option")


 ## Sample example   
script = "Se7en"
# players = ["Liza","Madi", "Rita", "Pedro", "Jed", "Oli", "Rowan", "Gana"]
# players = ["Liza","Madi", "Rita", "Pedro", "Jed", "Oli", "Rowan", "Gana", "Elia"]
players = ["Liza","Madi", "Rita", "Pedro", "Jed", "Oli", "Rowan", "Gana", "Elia", "Alona"]
# players = ["Liza","Madi", "Rita", "Pedro", "Jed", "Oli", "Rowan", "Gana", "Elia", "Alona", "Rowan2", "George"]

assignments(script, players)
