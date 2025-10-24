##Storing character states while in play

from character_classes import *

import pandas as pd

first_night_order = ["Lord Of Typhon", "Kazali", "Boffin", "Philosopher", "Alchemist", "Poppy Grower", "Yaggababble", "Magician", "Snitch", "Lunatic",
                     "Summoner", "King", "Sailor", "Marionette", "Engineer", "Preacher", "Lil Monsta", "Lleech", "Xaan", "Posioner", "Widow", "Courtier",
                     "Wizard", "Snake Charmer", "Godfather", "Organ Grinder", "Devil's Advocate", "Evil Twin", "Witch", "Cerenovus", "Fearmonger", "Harpy"
                     "Mezepheles", "Pukka", "Pixie", "Huntsman", "Damsel", "Amnesiac", "Washerwoman", "Librarian", "Investigator", "Chef", "Empath", "Fortune Teller",
                     "Butler", "Grandmother", "Clockmaker", "Dreamer", "Seamstress", "Steward", "Knight", "Noble", "Balloonist", "Shugenja", "Village Idiot",
                     "Bounty Hunter", "Nightwatchman", "Cult Leader", "Spy", "Ogre", "High Priestess", "General", "Chambermaid", "Mathematician", "Leviathan", "Vizier"]
other_night_order = ["Philosopher", "Poppy Grower", "Sailor", "Engineer", "Preacher", "Xaan", "Poisoner", "Courtier", "Innkeeper", "Wizard", "Gambler", "Acrobat",
                     "Snake Charmer", "Monk", "Organ Grinder", "Devil's Advocate", "Witch", "Cerenovus", "Pit Hag", "Fearmonger", "Harpy", "Mezepheles,"
                     "Scarlet Woman", "Summoner", "Lunatic", "Exorcist", "Lycanthrope", "Legion", "Imp", "Zombuul", "Pukka", "Shabaloth", "Po", "Fang Gu", "No Dashii",
                     "Vortox", "Lord Of Typhon", "Vigormortis", "Ojo", "Al Hadikhia", "Lleech", "Lil Monta", "Yaggababble", "Kazali", "Assassin", "Godfather",
                     "Gossip", "Hatter", "Barber", "Sweetheart", "Sage", "Banshee", "Professor", "Choirboy", "Huntsman", "Damsel", "Amnesiac", "Farmer",
                     "Tinker", "Moonchild", "Grandmother", "Ravenkeeper", "Empath", "Fortune Teller", "Undertaker", "Dreamer", "Flowergirl", "Town Crier",
                     "Oracle", "Seamstress", "Juggler", "Balloonist", "Village Idiot", "King", "Bounty Hunter", "Nightwatchman", "Cult Leader", "Butler",
                     "Spy", "High Priestess", "General", "Chambermaid", "Mathematician", "Leviathan"]



assignments = pd.DataFrame([
    {'player': 'Madi',    'character': 'Cult Leader',     'role_type': 'Minion',   'win_probability': 0.42, 'team': 'Evil', 'drunk': '_'},
    {'player': 'Rita',    'character': 'Pukka',           'role_type': 'Demon',    'win_probability': 0.38, 'team': 'Evil', 'drunk': '_'},
    {'player': 'Pedro',   'character': 'Banshee',         'role_type': 'Minion',   'win_probability': 0.45, 'team': 'Evil', 'drunk': '_'},
    {'player': 'Jed',     'character': 'Pixie',           'role_type': 'Townsfolk','win_probability': 0.61, 'team': 'Good', 'drunk': '_'},
    {'player': 'Oli',     'character': 'Alsaahir',        'role_type': 'Townsfolk','win_probability': 0.66, 'team': 'Good', 'drunk': '_'},
    {'player': 'Rowan2',  'character': 'Organ Grinder',   'role_type': 'Outsider', 'win_probability': 0.53, 'team': 'Good', 'drunk': '_'},
    {'player': 'Gana',    'character': 'Empath',          'role_type': 'Townsfolk','win_probability': 0.59, 'team': 'Good', 'drunk': '_'},
    {'player': 'Grace',   'character': 'Courtier',        'role_type': 'Townsfolk','win_probability': 0.64, 'team': 'Good', 'drunk': '_'},
    {'player': 'Alona',   'character': 'Washerwoman',     'role_type': 'Townsfolk','win_probability': 0.62, 'team': 'Good', 'drunk': '_'}
])


characters_df = pd.DataFrame([
    {'character_id': 1,  'name': 'Cult Leader',       'alignment': 'Evil',  'role_type': 'Minion',    'base_strength': 45, 'forced_evil': False},
    {'character_id': 2,  'name': 'Pukka',             'alignment': 'Evil',  'role_type': 'Demon',     'base_strength': 50, 'forced_evil': False},
    {'character_id': 3,  'name': 'Banshee',           'alignment': 'Evil',  'role_type': 'Minion',    'base_strength': 47, 'forced_evil': False},
    {'character_id': 4,  'name': 'Pixie',             'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 52, 'forced_evil': False},
    {'character_id': 5,  'name': 'Alsaahir',          'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 55, 'forced_evil': False},
    {'character_id': 6,  'name': 'Organ Grinder',     'alignment': 'Good',  'role_type': 'Outsider',  'base_strength': 48, 'forced_evil': False},
    {'character_id': 7,  'name': 'Empath',            'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 53, 'forced_evil': False},
    {'character_id': 8,  'name': 'Courtier',          'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 54, 'forced_evil': False},
    {'character_id': 9,  'name': 'Washerwoman',       'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 51, 'forced_evil': False},
    {'character_id': 10, 'name': 'Kazali',            'alignment': 'Evil',  'role_type': 'Demon',     'base_strength': 49, 'forced_evil': False},
    {'character_id': 11, 'name': 'Summoner',          'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 50, 'forced_evil': False},
    {'character_id': 12, 'name': 'Xaan',              'alignment': 'Good',  'role_type': 'Outsider',  'base_strength': 46, 'forced_evil': False},
    {'character_id': 13, 'name': 'Village Idiot',     'alignment': 'Good',  'role_type': 'Outsider',  'base_strength': 44, 'forced_evil': False},
    {'character_id': 14, 'name': 'Alchemist',         'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 56, 'forced_evil': False},
    {'character_id': 15, 'name': 'Spy',               'alignment': 'Evil',  'role_type': 'Minion',    'base_strength': 46, 'forced_evil': False},
    {'character_id': 16, 'name': 'Imp',               'alignment': 'Evil',  'role_type': 'Demon',     'base_strength': 50, 'forced_evil': False},
    {'character_id': 17, 'name': 'Pit Hag',           'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 57, 'forced_evil': False},
    {'character_id': 18, 'name': 'Fortune Teller',    'alignment': 'Good',  'role_type': 'Townsfolk', 'base_strength': 54, 'forced_evil': False},
    {'character_id': 19, 'name': 'Poisoner',          'alignment': 'Evil',  'role_type': 'Minion',    'base_strength': 48, 'forced_evil': False},
    {'character_id': 20, 'name': 'Baron',             'alignment': 'Evil',  'role_type': 'Minion',    'base_strength': 47, 'forced_evil': False}
])



# courtier = Courtier(assignments_df=assignments, characters_df=characters_df)
# courtier.current_state()
# print(courtier.info("setup"))
# print(courtier.info("firstnight"))

alchemist = CultLeader(assignments_df=assignments,characters_df=characters_df)
print(alchemist.info("setup"))
