import random
from pulp import LpVariable, lpSum, LpBinary, value


# ----------------------------
# Utility
# ----------------------------
def _binary_var(name, prob, x, char_index, players):
    """Helper to create a binary var that is 1 if the character is assigned."""
    var = LpVariable(name, cat="Binary")
    prob += lpSum(x[i][char_index] for i in range(len(players))) == var
    return var

# ----------------------------
# Character Constraints
# ----------------------------

def balloonist_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("balloonist_in_play", prob, x, char_index, players)
    shift = random.choice([0, 1])
    return {
        "Outsider": player_requirements['Outsider'] + shift * var,
        "Townsfolk": player_requirements['Townsfolk'] - shift * var,
        "_log": f"Balloonist → Outsiders +{shift}, Townsfolk -{shift}"
    }

def bounty_hunter_constraint(prob, x, characters, players, player_requirements, bh_index):
    num_players = len(players)

    # Candidate pool: only Good Townsfolk/Outsiders, EXCLUDING the BH themself
    valid_targets = characters[
        (characters['alignment'] == 'Good') &
        (characters['role_type'].isin(['Townsfolk'])) &
        (characters.index != bh_index)   # <-- exclude BH
    ].index.tolist()

    if not valid_targets:
        return {"_log": "Bounty Hunter present but no valid targets in script"}

    # Binary vars for target choice
    target_vars = {j: LpVariable(f"bh_target_{j}", cat=LpBinary) for j in valid_targets}

    # Presence variable: BH in play
    bh_in_play = lpSum(x[i][bh_index] for i in range(num_players))

    # Exactly one target iff BH is in play
    prob += lpSum(target_vars[j] for j in valid_targets) == bh_in_play

    # Link target choice to assignment
    for j in valid_targets:
        assigned_j = lpSum(x[i][j] for i in range(num_players))
        prob += assigned_j >= target_vars[j]
        prob += assigned_j <= 1

    if 'forced_evil' not in characters.columns:
        characters['forced_evil'] = False

    def hook(characters_df, players_df):
        chosen = None
        for j in valid_targets:
            if value(target_vars[j]) == 1:
                chosen = j
                break
        if chosen is not None:
            characters_df.loc[chosen, 'forced_evil'] = True
            return f"Bounty Hunter target: {characters_df.loc[chosen,'name']} (forced Evil)"
        if value(bh_in_play) == 0:
            return "Bounty Hunter not in play (no target)"
        return "Bounty Hunter target not resolved"

    return {
        "_log": "Bounty Hunter → target chosen iff BH in play; target must be assigned",
        "_hook": hook
    }




def choirboy_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("choirboy_in_play", prob, x, char_index, players)
    king_index = characters[characters['name'] == 'King'].index[0]
    prob += lpSum(x[i][king_index] for i in range(len(players))) >= var
    return {"_log": "Choirboy → King must also be in play"}

def huntsman_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("huntsman_in_play", prob, x, char_index, players)
    damsel_index = characters[characters['name'] == 'Damsel'].index[0]
    prob += lpSum(x[i][damsel_index] for i in range(len(players))) >= var
    return {"_log": "Huntsman → Damsel must also be in play"}


def village_idiot_constraint(prob, x, characters, players, player_requirements, _):
    """
    Village Idiot:
    - Between 0 and 3 inclusive can be assigned in a game.
    - If 2 or more are in play, one of the assigned players is drunk.
    """
    num_players = len(players)

    # All indices for Village Idiot variants (e.g. Village Idiot, Village Idiot 2, etc.)
    vi_indices = characters[characters['name'].str.startswith('Village Idiot')].index.tolist()

    # Count how many are assigned
    vi_count = lpSum(x[i][j] for i in range(num_players) for j in vi_indices)

    # Enforce between 0 and 3
    prob += vi_count <= 3

    def hook(characters_df, players_df):
        assigned_pairs = []
        for i in range(len(players_df)):
            for j in vi_indices:
                if x[i][j].value() == 1:
                    assigned_pairs.append((i, j))

        if len(assigned_pairs) >= 2:
            # Randomly choose one of the assigned VIs to be drunk
            drunk_player, drunk_char = random.choice(assigned_pairs)
            players_df.loc[drunk_player, 'drunk'] = True
            # Reduce their effective strength so balancing accounts for it
            characters_df.loc[drunk_char, 'base_strength'] = 15.0
            return f"Village Idiot → {players_df.loc[drunk_player,'name']} is drunk (strength reduced)"
        elif len(assigned_pairs) == 1:
            return "Village Idiot → in play (no drunk applied)"
        return "Village Idiot not in play"

    return {
        "_log": "Village Idiot → 0–3 allowed, if ≥2 then one player is drunk",
        "_hook": hook
    }


def hermit_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("hermit_in_play", prob, x, char_index, players)
    shift = random.choice([0, 1])
    return {
        "Outsider": player_requirements['Outsider'] - shift * var,
        "Townsfolk": player_requirements['Townsfolk'] + shift * var,
        "_log": f"Hermit → Outsiders -{shift}, Townsfolk +{shift}"
    }


def baron_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("baron_in_play", prob, x, char_index, players)
    return {
        "Outsider": player_requirements['Outsider'] + 2 * var,
        "Townsfolk": player_requirements['Townsfolk'] - 2 * var,
        "_log": "Baron → Outsiders +2, Townsfolk -2"
    }

def godfather_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("godfather_in_play", prob, x, char_index, players)
    shift = random.choice([-1, 1])
    return {
        "Outsider": player_requirements['Outsider'] + shift * var,
        "Townsfolk": player_requirements['Townsfolk'] - shift * var,
        "_log": f"Godfather → Outsiders {shift:+}, Townsfolk {(-shift):+}"
    }


# Summoner: -1 Demon, +1 Townsfolk
def summoner_constraint(prob, x, characters, players, player_requirements, char_index):
    """
    Summoner: if in play, reduce Demon count by 1 and increase Townsfolk by 1.
    """
    num_players = len(players)

    # Binary variable: 1 if Summoner is assigned to any player
    summoner_in_play = lpSum(x[i][char_index] for i in range(num_players))

    # Return adjusted requirements keyed by role_type
    return {
        "Demon": player_requirements['Demon'] - summoner_in_play,
        "Townsfolk": player_requirements['Townsfolk'] + summoner_in_play,
        "_log": "Summoner → Demons -1, Townsfolk +1"
    }


# Xaan: Outsiders set to random 1–4
def xaan_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("xaan_in_play", prob, x, char_index, players)
    outsiders = random.randint(1, 4)
    return {
        "Outsider": outsiders * var,
        "_log": f"Xaan → Outsiders set to {outsiders}"
    }

# Fang Gu: +1 Outsider, -1 Townsfolk
def fanggu_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("fanggu_in_play", prob, x, char_index, players)
    return {
        "Outsider": player_requirements['Outsider'] + 1 * var,
        "Townsfolk": player_requirements['Townsfolk'] - 1 * var,
        "_log": "Fang Gu → Outsiders +1, Townsfolk -1"
    }

# Kazali: No Minions, replace with random mix of Townsfolk/Outsiders
def kazali_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("kazali_in_play", prob, x, char_index, players)
    missing_minions = player_requirements['Minion']
    # Random split between Townsfolk and Outsiders
    extra_townsfolk = random.randint(0, missing_minions)
    extra_outsiders = missing_minions - extra_townsfolk
    return {
        "Minion": 0,
        "Townsfolk": player_requirements['Townsfolk'] + extra_townsfolk * var,
        "Outsider": player_requirements['Outsider'] + extra_outsiders * var,
        "_log": f"Kazali → Minions replaced with {extra_townsfolk} Townsfolk + {extra_outsiders} Outsiders"
    }

# Lil' Monsta: -1 Demon, +1 Minion, one Minion babysits
def lilmonsta_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("lilmonsta_in_play", prob, x, char_index, players)
    def hook(characters, players):
        minion_indices = characters[characters['role_type'] == 'Minion'].index.tolist()
        if minion_indices:
            babysitter_index = random.choice(minion_indices)
            characters.loc[babysitter_index, 'base_strength'] += 20
            return f"Lil' Monsta → Minion '{characters.loc[babysitter_index,'name']}' babysits (strength boosted)"
        return "Lil' Monsta in play but no Minion available"
    return {
        "Demon": player_requirements['Demon'] - 1 * var,
        "Minion": player_requirements['Minion'] + 1 * var,
        "_log": "Lil' Monsta → Demons -1, Minions +1",
        "_hook": hook
    }

# Lord of Typhon: No Minions, replace with Townsfolk/Outsiders, neighbours become Minions
def lord_of_typhon_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("lord_typhon_in_play", prob, x, char_index, players)
    missing_minions = player_requirements['Minion']
    extra_townsfolk = random.randint(0, missing_minions)
    extra_outsiders = missing_minions - extra_townsfolk
    def hook(characters, players):
        # Find Lord of Typhon's assigned player index
        lord_index = char_index
        # Neighbours in circular seating
        left = (lord_index - 1) % len(players)
        right = (lord_index + 1) % len(players)
        # Force them to be Minions
        characters.loc[left, 'role_type'] = 'Minion'
        characters.loc[right, 'role_type'] = 'Minion'
        characters.loc[left, 'alignment'] = 'Evil'
        characters.loc[right, 'alignment'] = 'Evil'
        return f"Lord of Typhon → Neighbours '{players.loc[left,'name']}' and '{players.loc[right,'name']}' set as Minions"
    return {
        "Minion": 0,
        "Townsfolk": player_requirements['Townsfolk'] + extra_townsfolk * var,
        "Outsider": player_requirements['Outsider'] + extra_outsiders * var,
        "_log": f"Lord of Typhon → Minions replaced with {extra_townsfolk} Townsfolk + {extra_outsiders} Outsiders, neighbours become Minions",
        "_hook": hook
    }

# Vigormortis: -1 Outsider, +1 Townsfolk
def vigormortis_constraint(prob, x, characters, players, player_requirements, char_index):
    var = _binary_var("vigormortis_in_play", prob, x, char_index, players)
    return {
        "Outsider": player_requirements['Outsider'] - 1 * var,
        "Townsfolk": player_requirements['Townsfolk'] + 1 * var,
        "_log": "Vigormortis → Outsiders -1, Townsfolk +1"
    }
# ----------------------------
# Registry
# ----------------------------
character_constraints = {
    "Balloonist": balloonist_constraint,
    "Bounty Hunter": bounty_hunter_constraint,
    "Choirboy": choirboy_constraint,
    "Huntsman": huntsman_constraint,
    "Village Idiot": village_idiot_constraint,
    "Hermit": hermit_constraint,
    "Baron": baron_constraint,
    "Godfather": godfather_constraint,
    "Summoner": summoner_constraint,
    "Xaan": xaan_constraint,
    "Fang Gu": fanggu_constraint,
    "Kazali": kazali_constraint,
    "Lil' Monsta": lilmonsta_constraint,
    "Lord of Typhon": lord_of_typhon_constraint,
    "Vigormortis": vigormortis_constraint

}



########################## CHARACTER CONSTRAINTS ##########################
## ATHEIST & LEGION BEING IGNORED DUE TO BEING EXPERIMENTAL ##
# Balloonist   
    # +0/+1 outsiders, -0/-1 townsfolk
        # Randomly choose which

# Bounty hunter
    # 1 townsfolk is actually evil
        # Need to treat townsfolk as evil in order to balance

# Choirboy
    # If there is a choirboy in play, then the King must be in play

# Huntsman
    # If there is a huntsman in play, then the Damsel must be in play

# Village idiot
    # There are 0-3 village idiots in play
        # If there are 2 =< village idiots, one is drunk

# Hermit
    # -0/-1 outsiders, +0/+1 townsfolk
        # Randomly choose which

# Baron
    # +2 outsiders, -2 townsfolk

# Godfather
    # -1/+1 outsiders, +1/-1 townsfolk

# Summoner
    # -1 demons, +1 townsfolk

# Xaan
    # x outsiders 
        # x being any number from 1-4 (probably)

# Fang Gu
    # +1 outsider, -1 townsfolk

# Kazali
    # No minion in play, instead the minion requirements are replaced with a random combination of townsfolk and outsiders to make up the number of minions missing

# Lil' monsta
    # -1 demon, +1 minion 
        # Randomly assign one of the minions to be babysitting the lil' monsta  

# Lord of Typhon
    # No minion in play, instead the minion requirements are replaced with a random combination of townsfolk and outsiders to make up the number of minions missing
    # Then the two players next to this character in the players array (looping round in a circle i.e. player i would be sat next to player i-1 and player 0) are minions, so need the minion chosen, and the game balanced accordingly

# Vigormorits 
    # -1 outsider, +1 townsfolk



###########################################################################