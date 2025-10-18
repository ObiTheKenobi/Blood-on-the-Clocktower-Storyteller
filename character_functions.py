## Character functions
## Specific outputs for each character as steps for the storyteller to take/checks to do
import pandas as pd
import pandas as pd
from typing import List

def extract_names(df: pd.DataFrame):
    """
    Return a single formatted string of names from df.
    Uses 'name' column first, then 'character'.
    Returns "DF empty" if df is None or empty.
    """
    if df is None or df.empty:
        return "DF empty"
    if 'name' in df.columns:
        temp = df['name'].astype(str).tolist()
        name_string = ' OR '.join([str(item) for item in temp])
        return name_string
    if 'character' in df.columns:
        temp = df['character'].astype(str).tolist()
        name_string = ' OR '.join([str(item) for item in temp])
        return name_string
    raise ValueError("DataFrame must contain 'name' or 'character' column")

def _df_to_name_list(df: pd.DataFrame):
    """
    Internal helper: returns a plain Python list of names from df.
    Prefers 'name' column, falls back to 'character'.
    """
    if df is None or df.empty:
        return []
    if 'name' in df.columns:
        return df['name'].astype(str).tolist()
    if 'character' in df.columns:
        return df['character'].astype(str).tolist()
    raise ValueError("DataFrame must contain 'name' or 'character' column")

def find_not_in_play(assignments_df: pd.DataFrame,
                     all_characters_df: pd.DataFrame,
                     role_type: str):
    """
    Return a list of names (strings) of characters of the requested role_type
    that are NOT present in assignments_df.
    Matching priority:
      1) match on character_id if both frames have it
      2) otherwise match assignments_df.character -> all_characters_df.name
    """
    # Validate role_type
    if role_type not in {'Townsfolk', 'Outsider', 'Minion', 'Demon'}:
        raise ValueError(f"Unknown role_type: {role_type}")

    # Filter all characters to requested role_type
    chars_of_role = all_characters_df[all_characters_df['role_type'] == role_type].copy()
    if chars_of_role.empty:
        return []

    # Match by character_id if available
    if 'character_id' in assignments_df.columns and 'character_id' in all_characters_df.columns:
        assigned_ids = set(assignments_df['character_id'].dropna().astype(int).unique())
        mask_not_assigned = ~chars_of_role['character_id'].dropna().astype(int).isin(assigned_ids)
        return _df_to_name_list(chars_of_role[mask_not_assigned].reset_index(drop=True))

    # Otherwise try name/character matching
    if 'character' in assignments_df.columns and 'name' in all_characters_df.columns:
        assigned_names = set(assignments_df['character'].dropna().astype(str).unique())
        mask_not_assigned = ~chars_of_role['name'].astype(str).isin(assigned_names)
        return _df_to_name_list(chars_of_role[mask_not_assigned].reset_index(drop=True))

    raise ValueError("assignments_df must contain 'character' or 'character_id' and all_characters_df must contain corresponding keys")

def find_not_in_play(assignments_df: pd.DataFrame,
                         all_characters_df: pd.DataFrame):
    """
    Return a list of names from all_characters_df that are NOT present in assignments_df,
    across every role_type. Uses the same matching priority as find_not_in_play.
    """
    if all_characters_df is None or all_characters_df.empty:
        return []

    # If both have character_id, prefer that
    if 'character_id' in assignments_df.columns and 'character_id' in all_characters_df.columns:
        assigned_ids = set(assignments_df['character_id'].dropna().astype(int).unique())
        mask_not_assigned = ~all_characters_df['character_id'].dropna().astype(int).isin(assigned_ids)
        return _df_to_name_list(all_characters_df[mask_not_assigned].reset_index(drop=True))

    # Otherwise try name/character matching
    if 'character' in assignments_df.columns and 'name' in all_characters_df.columns:
        assigned_names = set(assignments_df['character'].dropna().astype(str).unique())
        mask_not_assigned = ~all_characters_df['name'].astype(str).isin(assigned_names)
        return _df_to_name_list(all_characters_df[mask_not_assigned].reset_index(drop=True))

    raise ValueError("assignments_df must contain 'character' or 'character_id' and all_characters_df must contain corresponding keys")

def filterJinxes(jinxes, not_in_play_characters):
    filtered_jinxes = {}
    for character in not_in_play_characters:
        if jinxes.get(character, None) != None:
            filtered_jinxes[character] = jinxes.get(character)  


# Example usage
# not_in_play_minions = find_not_in_play(assignments_df=df, all_characters_df=characters_df, role_type='Minion')
#####################################################
def template_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = None
        jinxes = None
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = None
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = None
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do

#####################################################

def acrobat_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = None
        jinxes = None
        filtered_jinxes = None
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = None
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "Choose a player, if they are drunk or poisoned, mark acrobat as dead"
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do

def alchemist_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        not_in_play_minions = find_not_in_play(assigned, all_script_characters, "Minion")
        setup_rules = "Choose a not in play minion ability. Available minions:" + extract_names(not_in_play_minions)
        jinxes = {
            "Boffin":"If the alchemist has the boffin ability, the alchemist does not learn what ability the demon has",
            "Marionette":"Alchemist learns they are the marionette and therefore must be sat next to the demon/recluse",
            "Mastermind":"Mastermind is guaranteed not in play, and alchemist has no mastermind ability",
            "Orang Grinder":"If alchemist has organ grinder ability, then the organ grinder is in play. If both the alchemist and organ gridner are sober, both are drunk",
            "Spy":"Alchemist does not have spy ability, and a spy is put into play. Each day, after execution, the alchemist can publicy guess a living player as the spy. If correct, the demon must choose the spy tonight.",
            "Summoner":"Alchemist does not get bluffs, and chooses which demon but not which player. If they die before this happens, evil wins [REMOVE DEMON]",
            "Widow":"Alchemist does not have widow ability, and a widow is put into play. Each day, after execution, the alchemist can publicy guess a living player as the widow. If correct, the demon must choose the widow tonight.",
            "Wraith":"Alchemist does not have wraith ability, and a wraith is put into play. Each day, after execution, the alchemist can publicy guess a living player as the wraith. If correct, the demon must choose the wraith tonight."
        }
        filtered_jinxes = filterJinxes(jinxes, not_in_play_minions) 
        return [setup_rules, filtered_jinxes]
    
    elif info_type == "firstnight":
        first_night_to_do = "Please refer to the chosen minion. If any abilities chosen mess with gameplay, ask the player to choose otherwise"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "Please refer to the chosen minion. If any abilities chosen mess with gameplay, ask the player to choose otherwise"
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = "Please refer to the chosen minion. If any abilities chosen mess with gameplay, ask the player to choose otherwise"
        return death_to_do
      
def alsaahir_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = None
        jinxes = {"Vizier":"The alchemist must also guess which demon(s) are in play"}
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = None
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = None
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
    
def amnesiac_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = "Decide the ability of the amnesiac"
        jinxes = None
        filtered_jinxes = None
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = "Dependant on the chosen ability"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "Dependant on the chosen ability"
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
    
def artist_info(info_type, assigned=None, all_script_characters=None):
    return None

def atheist_info(info_type, assigned=None, all_script_characters=None):
    return None
    ##Template

def balloonist_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = "+0/+1 outsiders"
        jinxes = None
        filtered_jinxes = None
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = "Tell balloonist the name of a player"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "Tell balloonist the name of a player of a different type to last night"
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
    
def banshee_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = ""
        jinxes = {
            "Leviathan": "Banshee gains ability when they die (possibly by execution)",
            "Riot": "Banshee gains ability when they die (possibly by execution)",
            "Vortox":"Players still learn that the banshee has died"
        }
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = "None"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = None
        return other_nights_to_do
    elif info_type == "killed":
        death_to_do = "Announce the banshee's death to everyone. NOTE: banshee can now vote twice and nominate twice even when dead"
        return death_to_do
    elif info_type == "executed":
        death_to_do = None
        return death_to_do 
    
def bounty_hunter_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = "One townsfolk is evil (and is aware they are)"
        jinxes = {
            "Kazali":"An evil townsfolk is only created if the bounty hunter is still in play after the kazali acts",
        }
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters, "Demon"))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = "Choose an evil player to be known, and tell the bounty hunter"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "If the evil player who was known is dead, choose a new evil player"
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
    
def cannibal_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = None
        jinxes = {
            "Butler":"Cannibal learns they have gained the butler ability",
            "Juggler":"If the juggler died by execution on their first day, the living cannibal learns how many guesses the juggler got correct",
            "Poppy Grower":"Cannibal with poppy grower ability who dies/loses it causes minions and demon to learn each other",
            "Princess":"If the cannibal nominates, executes and kills the princess today, the demon doesn't kill tonight",
            "Zealot":"Cannibal learns they have gained the zealot ability"
        }
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = None
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "If a good player has been executed, the cannibal now has this ability (BUT IS NOT INFORMED WHICH ONE) and wakes when that character would normally. If an evil player is executed, the cannibal is poisoned, and should be woken when the evil character normally would and pretend they have this ability"
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do

def chambermaid_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = None
        jinxes = {
            "Mathematician":"Chambermaid learns if the mathematician wakes tonight or not even though the chambermaid wakes first"
        }
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters, "Townsfolk"))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = "Chambermaid chooses 2 alive players except themself, and inform them how many of them woke tonight"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "Chambermaid chooses 2 alive players except themself, and inform them how many of them woke tonight"
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
    
def chef_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = None
        jinxes = None
        filtered_jinxes = None
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = "Tell the chef how many pairs of neighbouring evil players there are"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = None
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
    
def choirboy_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = "King must be in play"
        jinxes = {
            "Kazali":"The kazali cannot choose the king to become a minion if a choirboy is in play"
        }
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters, "Demon"))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = None
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = "If the demon kills the king, tell the choirboy which player the demon is "
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
    
def clockmaker_info(info_type, assigned=None, all_script_characters=None):
    if info_type == "setup":
        setup_rules = None
        jinxes = {
            "Summoner":"If the summoner is in play, the clockmaker only gets info when the demon is created"
        }
        filtered_jinxes = filterJinxes(jinxes, find_not_in_play(assigned, all_script_characters))
        return [setup_rules, filtered_jinxes]
    elif info_type == "firstnight":
        first_night_to_do = "Tell the clockmaker how many steps from the demon the nearest minion is (1 = sat nexxt to)"
        return first_night_to_do
    elif info_type == "othernights":
        other_nights_to_do = None
        return other_nights_to_do
    elif info_type == "killed" or info_type == "executed":
        death_to_do = None
        return death_to_do
