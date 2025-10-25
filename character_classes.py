import pandas as pd

# ------------------ Utility Functions ------------------

def extract_names(df_or_list):
    """
    Return a single formatted string of names.
    Accepts either a pandas DataFrame or a list of strings.
    If DataFrame: uses 'name' column first, then 'character'.
    If list: joins items directly.
    Returns "DF empty" if input is None or empty.
    """
    if df_or_list is None:
        return "DF empty"

    # Handle list input
    if isinstance(df_or_list, list):
        if not df_or_list:
            return "DF empty"
        return ' OR '.join(str(item) for item in df_or_list)

    # Handle DataFrame input
    if isinstance(df_or_list, pd.DataFrame):
        if df_or_list.empty:
            return "DF empty"
        if 'name' in df_or_list.columns:
            return ' OR '.join(df_or_list['name'].astype(str).tolist())
        if 'character' in df_or_list.columns:
            return ' OR '.join(df_or_list['character'].astype(str).tolist())
        raise ValueError("DataFrame must contain 'name' or 'character' column")

    raise TypeError("Input must be a pandas DataFrame or a list")

def _df_to_name_list(df: pd.DataFrame):
    if df is None or df.empty:
        return []
    if 'name' in df.columns:
        return df['name'].astype(str).tolist()
    if 'character' in df.columns:
        return df['character'].astype(str).tolist()
    raise ValueError("DataFrame must contain 'name' or 'character' column")

def find_not_in_play(assignments_df: pd.DataFrame,
                     all_characters_df: pd.DataFrame,
                     role_type: str = None):
    if all_characters_df is None or all_characters_df.empty:
        return []

    if role_type:
        all_characters_df = all_characters_df[all_characters_df['role_type'] == role_type]

    if 'character_id' in assignments_df.columns and 'character_id' in all_characters_df.columns:
        assigned_ids = set(assignments_df['character_id'].dropna().astype(int).unique())
        mask = ~all_characters_df['character_id'].dropna().astype(int).isin(assigned_ids)
        return _df_to_name_list(all_characters_df[mask].reset_index(drop=True))

    if 'character' in assignments_df.columns and 'name' in all_characters_df.columns:
        assigned_names = set(assignments_df['character'].dropna().astype(str).unique())
        mask = ~all_characters_df['name'].astype(str).isin(assigned_names)
        return _df_to_name_list(all_characters_df[mask].reset_index(drop=True))

    raise ValueError("assignments_df must contain 'character' or 'character_id' and all_characters_df must contain corresponding keys")

def filterJinxes(jinxes, not_in_play_characters):
    return {char: jinxes[char] for char in not_in_play_characters if char in jinxes}

# ------------------ Base Character Class ------------------

class Character:
    def __init__(self, ability: bool, poisoned: bool, drunk: bool, dead: bool, team: str,
                 assignments_df: pd.DataFrame = None,
                 characters_df: pd.DataFrame = None):
        self.ability = ability
        self.poisoned = poisoned
        self.drunk = drunk
        self.dead = dead
        self.team = team,
        self.assignments_df = assignments_df
        self.characters_df = characters_df

    def set_ability(self, value): self.ability = bool(value)
    def set_poisoned(self, value): self.poisoned = bool(value)
    def set_drunk(self, value): self.drunk = bool(value)
    def set_dead(self, value): self.dead = bool(value)
    def set_team(self, value): self.team = str(value)

    def get_ability(self): return self.ability
    def get_poisoned(self): return self.poisoned
    def get_drunk(self): return self.drunk
    def get_dead(self): return self.dead
    def get_team(self): return self.team

    def current_state(self):
        print("Ability =", self.ability)
        print("Poisoned =", self.poisoned)
        print("Drunk =", self.drunk)
        print("Dead =", self.dead)
        print("Team =", self.team)

    def info(self, info_type: str):
        return None  # Default fallback


######################################################################################################
class Template(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

######################################################################################################
class Acrobat(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Choose a player, if they are drunk or poisoned, mark acrobat as dead"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do
        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Alchemist(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            not_in_play_minions = find_not_in_play(self.assignments_df, self.characters_df, "Minion")
            setup_rules = "Choose a not in play minion ability. Available minions: " + extract_names(not_in_play_minions)
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
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Please refer to the chosen minion. If any abilities chosen mess with gameplay, ask the player to choose otherwise"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Please refer to the chosen minion. If any abilities chosen mess with gameplay, ask the player to choose otherwise"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Please refer to the chosen minion. If any abilities chosen mess with gameplay, ask the player to choose otherwise"
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Please refer to the chosen minion. If any abilities chosen mess with gameplay, ask the player to choose otherwise"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Alsaahir(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {"Vizier":"The alchemist must also guess which demon(s) are in play"}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Alsaahir can publicly guess which players are minions and which players are demons "
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")
        
class Amnesiac(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Decide the ability of the amnesiac"
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Dependant on the chosen ability"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Dependant on the chosen ability"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Dependant on the chosen ability"
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Amnesiac asks about ability privately, can answer with either 'cold', 'warm', 'hot' or 'bingo'"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Artist(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        if info_type in {"killed", "executed"}:
            self.ability = False

        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Artist can privately ask any yes/no question, response being 'yes', 'no' or 'I don't know'"
            return day_to_do
        
        return None

class Atheist(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    ## NEEDS FILLING OUT ##
    def info(self, info_type: str):
        return None

class Balloonist(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "+0/+1 outsiders"
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell balloonist the name of a player"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell balloonist the name of a player of a different type to last night"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Banshee(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
            "Leviathan": "Banshee gains ability when they die (possibly by execution)",
            "Riot": "Banshee gains ability when they die (possibly by execution)",
            "Vortox":"Players still learn that the banshee has died"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type == "killed":
            death_to_do = "Announce the banshee's death to everyone. NOTE: banshee can now vote twice and nominate twice even when dead"
            return death_to_do

        elif info_type == "executed":
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class BountyHunter(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "One townsfolk is evil (and is aware they are)"
            jinxes = {
                "Kazali":"An evil townsfolk is only created if the bounty hunter is still in play after the kazali acts",
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Choose an evil player to be known, and tell the bounty hunter"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If the evil player who was known is dead, choose a new evil player"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Cannibal(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Butler":"Cannibal learns they have gained the butler ability",
                "Juggler":"If the juggler died by execution on their first day, the living cannibal learns how many guesses the juggler got correct",
                "Poppy Grower":"Cannibal with poppy grower ability who dies/loses it causes minions and demon to learn each other",
                "Princess":"If the cannibal nominates, executes and kills the princess today, the demon doesn't kill tonight",
                "Zealot":"Cannibal learns they have gained the zealot ability"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If a good player has been executed, the cannibal now has this ability (BUT IS NOT INFORMED WHICH ONE) and wakes when that character would normally. If an evil player is executed, the cannibal is poisoned, and should be woken when the evil character normally would and pretend they have this ability"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Chambermaid(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Mathematician":"Chambermaid learns if the mathematician wakes tonight or not even though the chambermaid wakes first"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Chambermaid chooses 2 alive players except themself, and inform them how many of them woke tonight"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Chambermaid chooses 2 alive players except themself, and inform them how many of them woke tonight"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Chef(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the chef how many pairs of neighbouring evil players there are"
                self.ability = False
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Choirboy(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "King must be in play"
            jinxes = {
                "Kazali":"The kazali cannot choose the king to become a minion if a choirboy is in play"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If the demon kills the king, tell the choirboy which player the demon is "
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Clockmaker(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Summoner":"If the summoner is in play, the clockmaker only gets info when the demon is created"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the clockmaker how many steps from the demon the nearest minion is (1 = sat nexxt to)"
                self.ability = False
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Courtier(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Summoner": "If the summoner is drunk on the 3rd night, the summoner chooses which demon, but storyteller chooses which player",
                "Vizier": "If the vizier loses their ability they learn this, if the vizier is executed while they have their ability, the vizier's team wins"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = "Ask the courtier if they would like to use their ability"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Ask the courtier if they would like to use their ability" 
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class CultLeader(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Boffin":"If the demon has the cult leader ability, they can't turn good due to this ability",
                "Pit Hag":"If the pit hag turns an evil player into the cult leader, they can't turn good due to their own ability"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "If both alive neighbours are good, cult leader is good, if both are evil, cult leader is evil, else choose good or evil"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If both alive neighbours are good, cult leader is good, if both are evil, cult leader is evil, else choose good or evil"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Dreamer(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the dreamer a good role and an evil role for the chosen player"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell the dreamer a good role and an evil role for the chosen player"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Empath(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell empath how many of their neighbours are evil"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell empath how many of their neighbours are evil"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Engineer(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Legion":"Legion and engineer cannot both be in play at the start of the game. If the engineer creates legion, most players (including all evil players) become legion"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Once per game, allow player option to choose which minions or which demon is in play"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Once per game, allow player option to choose which minions or which demon is in play"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Exorcist(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Leviathan":"Evil does not win when more than 1 good player has been executed, if the exorcist is alive and has ever successfully chosen the leviathan",
                "Riot":"If the exorcist chooses the riot on the 3rd night, minions do not become riot",
                "Yaggababble":"If the exorcist chooses the yaggababble, the yaggababble ability does not kill tonight"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Exorcist chooses one player, if they choose the demon, the demon is told which player the exorcist is, but cannot then use their ability that night (CANNOT CHOOSE SAME PLAYER 2 NIGHTS IN A ROW). Any other demon abilities still function (e.g. player attacked by pukka the previous night is still killed, the shabaloth can still regurgitate a player)"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Farmer(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Leviathan":"A farmer chosen by the leviathan uses their ability but does not die",
                "Riot":"A farmer chosen by the riot uses their ability but does not die"}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type == "executed":
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "killed":
            death_to_do = "An alive good player must become a farmer, and any ongoing effects of their old character must immediately end"
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Fisherman(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        if info_type in {"killed", "executed"}:
            self.ability = False

        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Once per game, the fisherman can privately visit the storyteller for advice to help their team win"
            return day_to_do
        return None

class Flowergirl(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell flowergirl whether the demon voted during that day"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Fool(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            if self.ability:
                death_to_do = "Fool is not actually dead, they remain alive"
                self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class FortuneTeller(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Choose one player to be the fortune teller's red herring"
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Get the fortune teller to point to 2 players, if either chosen is the demon/red herring, tell the fortune teller yes"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Get the fortune teller to point to 2 players, if either chosen is the demon/red herring, tell the fortune teller yes"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Gambler(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Gambler chooses a player (dead/alive/themself) and the character they think they are. If incorrect, the gambler dies"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class General(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell general which team you think is winning (Good/Evil/Neither)"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell general which team you think is winning (Good/Evil/Neither)"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Gossip(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If the gossip has said a true public statement today, kill a player"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Listen for the gossip's public statement during thes day"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Grandmother(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Choose a grandchild for the grandmother"
            jinxes = {
                "Leviathan":"If a leviathan is in play and the grandchild dies by execution, evil wins",
                "Riot":"If riot is in play and the grandchild dies during the day, the grandmother dies too"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the grandmother who their grandchild is"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If the granchild is dead, the grandmother dies too"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class HighPriestess(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the high priestess which player they should talk to the most (Good/Evil, Dead/Alive)"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell the high priestess which player they should talk to the most (Good/Evil, Dead/Alive)"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Huntsman(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Damsel must be in play"
            jinxes = {
                "Kazali":"If the kazali chooses the damsel to become a minion, and a huntsman is in play, a good player becomes the damsel",
                "Marionette":"If the marionette thinks they are the huntsman, the damsel is added"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Ask huntsman if they want to guess who the damsel is. If correct, the damsel becomes a not in play townsfolk"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Ask huntsman if they want to guess who the damsel is. If correct, the damsel becomes a not in play townsfolk"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Innkeeper(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Leviathan":"If a leviathan is in play, the innkeeper protected players are safe from all evil abilities",
                "Riot":"If riot is in play, the innkeeper protected player is safe from all evil abilities"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Innkeeper chooses 2 players, both are marked as safe (CANNOT DIE TONIGHT), one is marked drunk"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Investigator(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Vizier":"If the investigator learns the vizier is in play, the existence of the vizier is not announced by the storyteller"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the investigator the names of 2 players, one of which is a minion"
                self.ability = False
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Juggler(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Cannibal":"If the juggler guesses on their first day and dies by execution, tonight the living cannibal learns how many guesses the juggler got correct"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell the juggler how many of their guesses are correct"
                self.ability = False
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
    
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Listen for juggler's juggling"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class King(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Leviathan":"If the leviathan is in play, and at least one player is dead, the king learns an alive character each night",
                "Riot":"If riot is in play and at least one player is dead, the king learns an alive character each night"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = "Tell the demon who the king is"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If the daed equal/outnumber the living, tell the king one alive character"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Knight(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the knight 2 players which aren't the demon"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Librarian(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the librarian the name of 2 players, one of which is a named outsider. If there are no outsiders, tell them this"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Lycanthrope(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Mark one good player that will register as evil to the lycanthrope (faux paw)"
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Lycanthrope chooses a player - if good they die, and the demon cannot kill later tonight (but is woken as normal), else the demon works as normal"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Magician(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Lil Monsta":"Each night, the magician chooses a minion - if that minion and the lil monsta are alive, that minion babysits the lil monsta",
                "Spy":"When the spy sees the grimoire, the demon and magician's character tokens are removed",
                "Vizier":"If the vizier and magician are both in play, the demon does not learn the minions",
                "Widow":"When the widow sees the grimoire, the demon and magician's character tokens are removed",
                "Wraith":"Each day, after the execution phase, the living magician may publicly guess a living player as the wraith - if correct, the demon must choose the wraith tonight"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the magician, which player the minion is and which player the demon is. Tell the demon their minions are the players that are minions and the player that is the magician. The demon then gets the 3 bluffs. Tell the minions that the demons are both the player that is the demon and the player that is the magician"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Mathematician(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Chambermaid":"Chambermaid learns if the mathematician wakes tonight or not, even though the chambermaid wakes first",
                "Lunatic":"The mathematician learns if the lunatic attacks a different player than the real demon attacked"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = "Tell the mathematician how many abilities worked abnormally tonight"
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell the mathematician how many abilities worked abnormally tonight"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Mayor(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "None"
            jinxes = {
                "Leviathan":"If the leviathan is in play and no execution occurs on day 5. good wins",
                "Riot":"The mayor can choose to stop nominations. If they do so when only one riot is alive, good wins; else, evil wins"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "If only 3 players live and no execution occurs, the mayor's team wins"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If only 3 players live and no execution occurs, the mayor's team wins"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Another player might die instead (including dead players)"
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Minstrel(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Legion":"If legion died by execution today, legion keeps their ability, but the minstrel might learn they are legion"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = "If a minion has been executed, all other players are drunk unil dusk tomorrow"
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Monk(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Leviathan":"If leviathan is in play, the monk protected player is safe from all evil abilities",
                "Riot":"If riot is in play, the monk protected player is safe from all evil abilities"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Choose a player to be safe from the demon tonight"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Nightwatchman(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Choose whether they want another player to learn if they are the nightwatchman"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Choose whether they want another player to learn if they are the nightwatchman"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Noble(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the noble the names of 3 players, only 1 of which is evil"
                self.ability = False
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Oracle(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell the oracle how many dead players are evil"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Pacifist(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Choose whether executed good players die or not (this still counts as an execution and therefore no other nominations may happen)"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Philosopher(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Bounty Hunter":"If the philosopher gains the obunty hunter ability, a townsfolk might turn evil"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Philosopher chooses whether they want to become another good character. If this character is in play, the original one is drunk"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Philosopher chooses whether they want to become another good character. If this character is in play, the original one is drunk"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Character that was made drunk by the philosopher becomes sober"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Pixie(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = "Storyteller chooses an in play townsfolk, and if they are mad they are this character, they gain their ability when they die"
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If the pixie is mad they are the in play townsfolk, they gain the townsfolk's ability when player dies"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class PoppyGrower(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Lil Monsta":"Minions don't wake together, they are woken individually, until one of them chooses to babysit the lil' montsa",
                "Marionette":"When the poppy grower dies, the demon learns the marionette, but the marionette learns nothing",
                "Spy":"If the poppy grower is in play, the spy does not see the grimoire until the poppy grower dies",
                "Summoner":"If the poppy grower is alive when the summoner acts, the summoner chooses which demon, but the storyteller chooses which player",
                "Widow":"If the poppy grower is in play, the widow does not see the grimoire until the poppy grower dies"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = "Give the demon the bluffs, but don't tell the demon and minions who each other are"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Evil characters that are allowed to see the grimoire now can, and the demon and minion get to learn who each other are"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Preacher(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Legion":"If the preacher chooses legion, legion keeps their ability but the preacher might learn they are legion",
                "Summoner":"If the preacher chose the summoner on/before the 3rd night, the summoner chooses which demon, but the storyteller chooses which player",
                "Vizier":"If the vizier loses their ability, they learn this. If the vizier is executed while they have their ability, their team wins"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Preacher chooses a player - if a minion, they learn this and the minion loses their ability"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Preacher chooses a player - if a minion, they learn this and the minion loses their ability"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "All minions that lost their ability gain it back"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Princess(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Cannibal":"If the cannibal nominated, executed and killed the princess todya, the demon doesn't kill tonight",
                "Al Hadikhia":"If the princess nominated and executed a player on their 1st day, no one dies to the Al-Hadikhia ability tonight"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = ""
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "On the first day, if the princess nominated and executed a player, the demon doesn't kill tonight"
                self.ability = False
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Professor(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Professor can choose a dead player to resurrect once a game. If they are townsfolk, they are resurrected; if not nothing happens"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Ravenkeeper(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Leviathan":"Each night the leviathan chooses an alive player (different to previous nights) - a chosen ravenkeeper uses thei ability but does not die",
                "Riot":"Each night, the riot chooses an alive good player (different to previous nights) - a chosen ravenkeeper uses their ability but does not die"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type == "killed":
            death_to_do = "Ravenkeeper chooses a player and finds out which character they are"
            self.ability = False
            return death_to_do

        elif info_type == "executed":
            self.ability = False
            return None
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Sage(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Leviathan":"Each night, the leviathan chooses an alive good player (different to previous nights) - a chosen sage uses their ability but does not die",
                "Riot":"Each night, the riot chooses an alive good player (different to previous nights) - a chosen sage uses their ability but does not die"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type == "killed":
            death_to_do = "If the sage was killed by the demon, they learn it is 1 of 2 players"
            self.ability = False
            return death_to_do
        
        elif info_type == "executed":
            self.ability = False
            return None

        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Sailor(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Choose an alive player - either you or they are drunk until dusk - sailor can't die (murder/execution) while sober"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Choose an alive player - either you or they are drunk until dusk - sailor can't die (murder/execution) while sober"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Sailor can't die (murder/execution) when sober"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Savant(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Savant can privately visit the storyteller to learn 1 true thing, 1 false thing"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Seamstress(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Once per game, the seamstress can choose 2 players (dead/alive) (not themself) and learn whether they are the same alignment"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Once per game, the seamstress can choose 2 players (dead/alive) (not themself) and learn whether they are the same alignment"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Shugenja(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the shugenja whether their closest evil player is clockwise/anti-clockwise (if equidistant, its arbritrary)"
                self.ability = False
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Slayer(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Lleech":"If the slayer slays the lleech's host, the host dies"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Once per game, the slayer can publicly choose a player - if they are the demon, they die"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class SnakeCharmer(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Snake charmer chooses an alive player - a chosen demon swaps characters and alignments with you, and is then poisoned"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Snake charmer chooses an alive player - a chosen demon swaps characters and alignments with you, and is then poisoned"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Soldier(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Soldier is protected from all harmful effects of the demon's ability"
            jinxes = {
                "Kazali":"Kazali can choose that the soldier player is one of their evil minions",
                "Leviathan":"If the leviathan is in play, the soldier is safe from all evil abilities",
                "Riot":"If riot is in play, the soldier is safe from all evil abilities"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "killed":
            death_to_do = "Soldier cannot be killed by the demon (and is safe from all harmful effects of the demon's ability)"
            return death_to_do

        else:
            return None

class Steward(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the steward the name of a player that is good"
            return first_night_to_do

        else:
            return None

class TeaLady(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "If both alive neighbours of the tea lady are good, they can't die"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If both alive neighbours of the tea lady are good, they can't die"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class TownCrier(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tell the town crier whether a minion nominated today or not"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Undertaker(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "The undertaker learns which character died by execution today"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class VillageIdiot(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "There can be either 0/1/2/3 village idiots, if there is more than 1 village idiot, then one of them is drunk"
            jinxes = {
                "Boffin":"If there are less than 3 village idiots, the boffin can give the demon the village idiot ability",
                "Pit Hag":"If there are less than 3 village idiots, the pit-hag can create an extra village idiot - if so, the durnk village idiot might change"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "The village idiot chooses a player, and finds out whether that player is good or evil"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "The village idiot chooses a player, and finds out whether that player is good or evil"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Virgin(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "The 1st time the virgin is nominated, if the nominator is a townsfolk, they are executed immediately (proceed to night phase)"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Washerwoman(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "The washerwoman knows that 1 of 2 players is a particular townsfolk"
            return first_night_to_do

        else:
            return None

class Barber(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "The demon can now choose 2 players (not another demon (but can be themself)) to swap characters"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Butler(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Organ Grinder":"If the organ grinder is causing a hidden vote, the butler may raise their hand to vote, but their vote is only counted if their master voted too"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Get butler to choose a player that will be their master (butler can only vote when the master votes)"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Get butler to choose a different player from last night that will be their master (butler can only vote when the master votes)"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Damsel(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Marionette":"Marionette does not learn that a damsel is in play",
                "Spy":"If the spy is/has been in play, the damsel is poisoned",
                "Widow":"If the widow is/has been in play, the damsel is poisoned"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell every minion that the damsel is in play"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "If a minion publicly guesses which player is the damsel and is correct, evil wins; else, no more minions can guess who the damsel is"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Drunk(Character):
    def __init__(self, ability=True, poisoned=False, drunk=True, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Change the drunk character's token to be a different townsfolk (but they are still the drunk)"
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Golem(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "The golem can only nominate once a game. If the player they nominate is not the demon, that player dies immediately (nomination process continues)"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Goon(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "The 1st player to choose the goon with their ability is drunk immediately until dusk, and the goon becomes that player's alignment (tell the goon this)"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "The 1st player to choose the goon with their ability is drunk immediately until dusk, and the goon becomes that player's alignment (tell the goon this)"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Hatter(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Legion":"If the hatter dies and legion is in play, nothing happens. If the hatter dies and an evil player chooses legion, all current evil players become legion",
                "Leviathan":"If the hatter dies on/after day 5, the demon cannot choose leviathan",
                "Lil Monsta":"If a demon chooses lil' monsta, they also choose a minion to become and babysit lil' monsta tonight",
                "Summoner":"Summoner cannot create an in play demon. If the summoner creates a not in play demon, deaths tonight are arbritrary"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "The minion and demon players may choose minions and demon characters to be (cannot be the same character)"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Heretic(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Whoever wins, loses and whoever loses, wins, even if the heretic is dead (but not when drunk and poisoned)"
            jinxes = {
                "Baron":"Baron can only add 1 outsider, not 2",
                "Boffin":"Demon cannot have the heretic ability",
                "Godfather":"Only 1 jinxed character can be in play",
                "Lleech":"If the lleech poisoned the heretic then the lleech dies, the heretic remains poisoned",
                "Pit Hag":"A pit hag cannot create a heretic",
                "Spy":"Only 1 jinxed character can be in play",
                "Widow":"Only 1 jinxed character can be in play"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Whoever wins, loses and whoever loses, wins, even if the heretic is dead (but not when drunk and poisoned)"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Hermit(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "-0/-1 outsider, hermit has all outsider abilities"
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Run all outsider abilities for the hermit"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Run all outsider abilities for the hermit"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Run all outsider abilities for the hermit"
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Run all outsider abilities for the hermit"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Klutz(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type == "executed":
            death_to_do = "Klutz must choose 1 alive player (wihtin 1/2 mins) - if that player is evil, the klutz's team loses; else continue play"
            self.ability = False
            return death_to_do
        
        elif info_type == "killed":
            death_to_do = "Klutz must choose 1 alive player first thing in the morning- if that player is evil, the klutz's team loses; else continue play"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Lunatic(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Change the lunatic's token to be a demon on the script"
            jinxes = {
                "Mathematician":"Mathematician learns if the lunatic attacks a different player(s) than the real demon attacked"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tell the lunatic their demon bluffs and their minions. Tell the demon which player is the lunatic "
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Wake the lunatic as though they are the demon. Tell the demon who the lunatic chose"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Moonchild(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type == "executed":
            death_to_do = "The moonchild must publicly choose 1 alive player before night. If that player was good, they die"
            self.ability = False
            return death_to_do
        
        elif info_type == "killed":
            death_to_do = "The moonchild must publicly choose 1 alive player in the morning. If that player was good, they die"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Mutant(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "If the mutant is mad about being an outsider, there is a chance the mutant is executed (max one execution per day)"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "If the mutant is mad about being an outsider, there is a chance the mutant is executed (max one execution per day)"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "If the mutant is mad about being an outsider, there is a chance the mutant is executed (max one execution per day)"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Ogre(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Pit Hag":"If the pit hag turns an evil player into the ogre, they can't turn good due to their own ability",
                "Recluse":"If the recluse registers as evil to the ogre, the ogre learns that they are evil",
                "Spy":"Spy registers as evil to the ogre"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Ogre chooses one player, and then becomes their alignment (they don't find out which) even if drunk/poisoned"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class PlagueDoctor(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Baron":"If the storyteller gains the baron ability, up to 2 players become not in play outsiders",
                "Boomdandy":"If the plague doctor is executed and the storyteller would gain the boomdandy ability, the boomdandy ability triggers immediately",
                "Evil Twin":"The storyteller cannot gain the evil twin ability if the plague doctor dies",
                "Fearmonger":"If the plague doctor dies, a living minion gains the fearmonger ability in addition to their own ability and learns this",
                "Goblin":"If the plague doctor dies, a living minion gains the goblin ability in addition to their own ability, and learns this",
                "Marionette":"If the demon has a neighbour who is alive and a townsfolk/outsider when the plague doctor dies, that player becomes an evil marionette. If there is already an extra evil player, this does not happen",
                "Scarlet Woman":"If the plague doctor dies, a living minion gains the scarlet woman ability in addition to their own ability and learns this",
                "Spy":"If the plague doctor dies, a living minion gains the spy ability in addition to their own ability, and learns this",
                "Wraith":"If the plague doctor dies, a living minion gains the wraith ability in addition to their own ability, and learns this"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Storyteller gains a minion ability, and when the minion would act, that is when the storyteller acts. The storyteller is not a player"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Politician(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "If the politician was most responsible for their team losing, they change alignment and win, even if dead"
            jinxes = {
                "Pit Hag":"If the pit hag turns an evil player into the politician, they can't turn good due to their own ability",
                "Vizier":"The politican might register as evil to the vizier"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "If the politician was most responsible for their team losing, they change alignment and win, even if dead"
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "If the politician was most responsible for their team losing, they change alignment and win, even if dead"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Puzzlemaster(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = "Make someone as the drunk"
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "If the puzzlemaster guesses who the puzzlemaster's drunk is correctly then they learn the demon player; if wrong they get false info"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Recluse(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Ogre":"If the recluse registers as evil to the ogre, the ogre learns that they are evil"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Recluse might register as evil and as a minion/demon, even if dead"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Recluse might register as evil and as a minion/demon, even if dead"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Recluse might register as evil and as a minion/demon, even if dead"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Saint(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type == "executed":
            death_to_do = "The saint's team loses"
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Snitch(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Marionette":"Marionette does not learn 3 not in play characters, the demon learns an extra 3 instead"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Every minion gets 3 bluffs"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Sweetheart(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = "Make 1 player drunk for the rest of the game"
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = None
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Tinker(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {}
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = "Tinker can die at any time"
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = "Tinker can die at any time"
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "Tinker can die at any time"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")

class Zealot(Character):
    def __init__(self, ability=True, poisoned=False, drunk=False, dead=False, team="Good",
                 assignments_df=None, characters_df=None):
        super().__init__(ability, poisoned, drunk, dead, team, assignments_df, characters_df)

    def info(self, info_type: str):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Legion":"Zealot might register as evil to legion's ability",
                "Vizier":"Zealot might register as evil to the vizier"
            }
            not_in_play = find_not_in_play(self.assignments_df, self.characters_df)
            filtered_jinxes = filterJinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            if self.ability:
                first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            other_nights_to_do = None
            if self.ability:
                other_nights_to_do = None
            return other_nights_to_do

        elif info_type in {"killed", "executed"}:
            death_to_do = None
            self.ability = False
            return death_to_do
        
        elif info_type == "daytime":
            day_to_do = None
            if self.ability:
                day_to_do = "If there are 5 or more players alive, the zealot must vote for every nomination"
            return day_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")










