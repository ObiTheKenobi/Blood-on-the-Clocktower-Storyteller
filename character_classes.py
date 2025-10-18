## changing functions to classes

import pandas as pd

class Character:
    """
    Character helper that stores assignment and script character DataFrames.
    Use instance methods which operate on the stored data.
    """

    def __init__(self, assigned_df=None, all_characters_df=None):
        self.assigned_df = assigned_df if assigned_df is not None else pd.DataFrame()
        self.all_characters_df = all_characters_df if all_characters_df is not None else pd.DataFrame()

    # -------------------------
    # DataFrame extraction helpers
    # -------------------------
    @staticmethod
    def extract_names(df):
        if df is None or df.empty:
            return "DF empty"
        if 'name' in df.columns:
            return ' OR '.join(df['name'].astype(str).tolist())
        if 'character' in df.columns:
            return ' OR '.join(df['character'].astype(str).tolist())
        raise ValueError("DataFrame must contain 'name' or 'character' column")

    @staticmethod
    def _df_to_name_list(df):
        if df is None or df.empty:
            return []
        if 'name' in df.columns:
            return df['name'].astype(str).tolist()
        if 'character' in df.columns:
            return df['character'].astype(str).tolist()
        raise ValueError("DataFrame must contain 'name' or 'character' column")

    # -------------------------
    # Core matching helpers (use stored frames)
    # -------------------------
    def find_not_in_play(self, role_type=None):
        """
        Return names from all_characters_df that are not present in assigned_df.
        If role_type is provided, filter all_characters_df by role_type first.
        Matching priority:
          1) character_id (if present in both)
          2) assignments_df.character -> all_characters_df.name
        """
        assigned = self.assigned_df
        all_chars = self.all_characters_df

        if all_chars is None or all_chars.empty:
            return []

        chars = all_chars
        if role_type is not None:
            if role_type not in {'Townsfolk', 'Outsider', 'Minion', 'Demon'}:
                raise ValueError(f"Unknown role_type: {role_type}")
            chars = chars[chars['role_type'] == role_type].copy()
            if chars.empty:
                return []

        # Prefer character_id matching
        if (assigned is not None
                and 'character_id' in assigned.columns
                and 'character_id' in chars.columns):
            assigned_ids = set(assigned['character_id'].dropna().astype(int).unique())
            mask_has_id = chars['character_id'].notna()
            mask_not_assigned = mask_has_id & (~chars['character_id'].astype(int).isin(assigned_ids))
            return Character._df_to_name_list(chars[mask_not_assigned].reset_index(drop=True))

        # Otherwise try name/character matching
        if (assigned is not None
                and 'character' in assigned.columns
                and 'name' in chars.columns):
            assigned_names = set(assigned['character'].dropna().astype(str).unique())
            mask_not_assigned = ~chars['name'].astype(str).isin(assigned_names)
            return Character._df_to_name_list(chars[mask_not_assigned].reset_index(drop=True))

        raise ValueError("assignments_df must contain 'character' or 'character_id' and all_characters_df must contain corresponding keys")

    def filter_jinxes(self, jinxes, not_in_play_characters=None):
        """
        Return jinxes filtered to characters listed in not_in_play_characters.
        If not_in_play_characters is None, compute from stored frames across all roles.
        """
        not_in_play = not_in_play_characters
        if not_in_play is None:
            not_in_play = self.find_not_in_play()
        not_in_play_set = set(str(x) for x in not_in_play)
        return {char: text for char, text in jinxes.items() if char in not_in_play_set}
    def info(self):
        return None

#######################################################################################
class Template(Character):
    """
    Courtier subclass that provides courtier-specific info.
    The assigned and all_characters frames are taken from the Character base instance.
    The ability flag is persistent on the Courtier instance and can be toggled.
    """

    def __init__(self, assigned_df=None, all_characters_df=None, ability=True):
        super().__init__(assigned_df=assigned_df, all_characters_df=all_characters_df)
        self.ability = True

    def set_ability(self, value):
        self.ability = bool(value)

    def template_info(self, info_type):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = None
            not_in_play = self.find_not_in_play()
            filtered_jinxes = self.filter_jinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            first_night_to_do = None
            return first_night_to_do

        elif info_type == "othernights":
            if self.ability:
                other_nights_to_do = None
                return other_nights_to_do
            return None

        elif info_type == "killed" or info_type == "executed":
            death_to_do = None
            return death_to_do

        else:
            raise ValueError(f"Unknown info_type: {info_type}")
#######################################################################################

class Courtier(Character):

    def __init__(self, assigned_df=None, all_characters_df=None, ability=True):
        super().__init__(assigned_df=assigned_df, all_characters_df=all_characters_df)
        self.ability = True

    def set_ability(self, value):
        self.ability = bool(value)

    def info(self, info_type):
        info_type = str(info_type)

        if info_type == "setup":
            setup_rules = None
            jinxes = {
                "Summoner": "If the summoner is drunk on the 3rd night, the summoner chooses which demon, but storyteller chooses which player",
                "Vizier": "If the vizier loses their ability they learn this, if the vizier is executed while they have their ability, the vizier's team wins"
            }
            not_in_play = self.find_not_in_play()
            filtered_jinxes = self.filter_jinxes(jinxes, not_in_play)
            return [setup_rules, filtered_jinxes]

        elif info_type == "firstnight":
            return "Ask the courtier if they would like to use their ability"

        elif info_type == "othernights":
            if self.ability:
                return "Ask the courtier if they would like to use their ability"
            return None

        elif info_type == "killed" or info_type == "executed":
            return None

        else:
            raise ValueError(f"Unknown info_type: {info_type}")