## POST GAME DATA COLLECTION ##
import sqlite3
from rapidfuzz import process



## Tries to autocorrect incorrectly entered character names
def correct_spelling(input_str, valid_entries, threshold=10):
    match = process.extractOne(input_str, valid_entries, score_cutoff=threshold)
    return match[0] if match else None


## Compute the new strength of a character depending on how it performed throughout the game
def compute_adjusted_strength(character_id, decay_factor=0.3):
    try:
        con = sqlite3.connect('clocktower.db') 
        cur = con.cursor() 
    except Exception as e:
        print(f'An error occurred: {e}.')
        exit()

    # Fetch historical base strength
    query = "SELECT base_strength FROM characters WHERE character_id = ?"
    cur.execute(query, (character_id,))
    historical_strength = cur.fetchone()[0]

    # Fetch recent games (e.g. last 10)
    query = """
    SELECT a.won, c.alignment
    FROM assignments a
    JOIN characters c ON a.character_id = c.character_id
    WHERE a.character_id = ?
    ORDER BY a.game_id DESC
    LIMIT 10
    """
    cur.execute(query, (character_id,))
    recent_games = cur.fetchall()

    # Fallback if there is no historical data
    if not recent_games:
        return historical_strength  

    # Compute recent win rate
    wins = sum([row[0] for row in recent_games])
    recent_win_rate = wins / len(recent_games)

    # Map win rate to strength, scaling ±25 around 50
    recent_strength = 50 + (recent_win_rate - 0.5) * 50  

    # Apply decay-based averaging
    adjusted_strength = round(decay_factor * recent_strength + (1 - decay_factor) * historical_strength, 2)


    query = """
    UPDATE characters
    SET base_strength = ?
    WHERE character_id = ?;
    """
    cur.execute(query, (adjusted_strength, character_id))
    con.commit()
    con.close()
    return round(adjusted_strength, 2)




## Update the elo of the people that played the game
def eloUpdate(game_id):
    k = 24  # Elo update factor

    try:
        con = sqlite3.connect('clocktower.db')
        cur = con.cursor()

        # Fetch all assignments for this game
        query = """
        SELECT player_id, team, won
        FROM assignments
        WHERE game_id = ?;
        """
        cur.execute(query, (game_id,))
        all_assignments = cur.fetchall()

        # Separate players by team
        good_ids = [pid for pid, team, _ in all_assignments if team == "Good"]
        evil_ids = [pid for pid, team, _ in all_assignments if team == "Evil"]

        # Fetch average Elo for each team
        if good_ids:
            cur.execute(f"SELECT AVG(elo_good) FROM players WHERE player_id IN ({','.join(map(str, good_ids))})")
            avg_good_elo = cur.fetchone()[0]
        else:
            avg_good_elo = 1500  # fallback

        if evil_ids:
            cur.execute(f"SELECT AVG(elo_evil) FROM players WHERE player_id IN ({','.join(map(str, evil_ids))})")
            avg_evil_elo = cur.fetchone()[0]
        else:
            avg_evil_elo = 1500  # fallback

        # Update Elo for each player
        for player_id, team, won in all_assignments:
            if team == "Good":
                cur.execute("SELECT elo_good FROM players WHERE player_id = ?", (player_id,))
                player_elo = cur.fetchone()[0]
                expected_score = 1 / (1 + 10 ** ((avg_evil_elo - player_elo) / 400))
                new_elo = int(player_elo + k * (won - expected_score))
                cur.execute("UPDATE players SET elo_good = ? WHERE player_id = ?", (new_elo, player_id))

            elif team == "Evil":
                cur.execute("SELECT elo_evil FROM players WHERE player_id = ?", (player_id,))
                player_elo = cur.fetchone()[0]
                expected_score = 1 / (1 + 10 ** ((avg_good_elo - player_elo) / 400))
                new_elo = int(player_elo + k * (won - expected_score))
                cur.execute("UPDATE players SET elo_evil = ? WHERE player_id = ?", (new_elo, player_id))

        con.commit()
        print("Elo ratings updated successfully.")

    except Exception as e:
        print(f"Elo update failed: {e}")
    finally:
        con.close()

## Main function
def dataCollection():
    players = []
    winning_team = str(input("Enter winning team (good/evil):   ")).capitalize()
    num_players = int(input("Enter number of players:   "))
    num_alive_players = int(input("Enter number of alive players:   "))

    try:
        con = sqlite3.connect('clocktower.db') 
        cur = con.cursor() 
    except Exception as e:
        print(f'An error occurred: {e}.')
        exit()
        


    script = str(input("Enter script/X if unknown name:   "))

    words = script.strip().split()
    for i in range(0,len(words)):
        if i == 0:
            script = words[i].capitalize()
        elif 1 <= i and i < len(words):
            script += "_" + words[i].lower()
        else:
            script += words[i].lower()

    if script == "x":
        script = None

        query = """
        INSERT INTO games (winning_team, player_count, players_alive)
        VALUES(?, ?, ?);
        """
    else:
        query = """
        SELECT script_id
        FROM scripts
        WHERE name = ?
        """
        cur.execute(query, (script,))
        script_id = int(cur.fetchall()[0][0])
        query = """
        INSERT INTO games (script_id, winning_team, player_count, players_alive)
        VALUES(?, ?, ?, ?);
        """
    cur.execute(query, (script_id, winning_team, num_players, num_alive_players))
    con.commit()

    query = """
    SELECT name
    FROM characters 
    JOIN script_characters ON characters.character_id = script_characters.character_id
    WHERE script_id = ?
    """

    cur.execute(query, (script_id,))
    valid_char_list = cur.fetchall()
    temp = zip(*valid_char_list)

    valid_char_list = list(temp)[0]
    
    query = """
    SELECT game_id
    FROM games
    ORDER BY game_id DESC
    LIMIT 1;
    """
    cur.execute(query)
    game_id = int(cur.fetchall()[0][0])

    con.close()

    logged_players = 0
    
    while logged_players < num_players:
        player_info = []
        player = str(input("Enter player name/x if done/add:   ")).capitalize()
        if player.lower() == "x":
            inputting = False
            break
        elif player.lower() == "add":
            new_player = str(input("Enter player name:   "))
            addPlayer(new_player)
        elif player.lower() == "de":
            players = de
            inputting = False
        else:
            players.append(player)

        try:
            con = sqlite3.connect('clocktower.db') 
            cur = con.cursor() 
        except Exception as e:
            print(f'An error occurred: {e}.')
            exit()



        query = """
        SELECT player_id
        FROM players
        WHERE name = ?;
        """
        
        cur.execute(query, (player,))
        player_id = cur.fetchall()
        if str(player_id) == "[]":
            print("Invalid player name")
            continue


        player_id = player_id[0][0]
        query = """
        SELECT *
        FROM assignments
        WHERE game_id = ? AND player_id = ?
        """
        cur.execute(query, (game_id, player_id))
        in_game = cur.fetchall()
        if str(in_game) != "[]":
            print("Player already in this game")
            continue
        


        valid_char = False
        no_correction = True
        while valid_char == False:
            if no_correction:
                char_name = str(input("Enter player's character:   "))
                char_name = " ".join(word.capitalize() for word in char_name.split())
            no_correction = True

            query = """
            SELECT character_id, alignment
            FROM characters
            WHERE name = ?;
            """

            
            cur.execute(query, (char_name,))
            char = cur.fetchall()


            if str(char) == "[]":
                print("Invalid character name")
                corr = correct_spelling(char_name, valid_char_list)
                corr = " ".join(word.capitalize() for word in corr.split())
                did_mean = str(input("Did you mean: " + str(corr) + "?   ")).lower()
                if did_mean == "yes" or did_mean == "y":
                    char_name = corr
                    no_correction = False
            else:
            
                char_id = char[0][0]
                char_align = char[0][1]

                query = """
                SELECT *
                FROM script_characters
                WHERE script_id = ? AND character_id = ?;
                """
                cur.execute(query, (script_id,char_id))
                char = cur.fetchall()
                if str(char) == "[]":
                    print("Character not in this script")
                    corr = correct_spelling(char_name, valid_char_list)
                    corr = " ".join(word.capitalize() for word in corr.split())
                    did_mean = str(input("Did you mean: " + str(corr) + "?   ")).lower()
                    if did_mean == "yes" or did_mean == "y":
                        char_name = corr
                        no_correction = False

                else:
                    valid_char = True
        
        team = str(input("Enter player's team:   ")).capitalize()
        
        if team != char_align:
            print("The", char_name.lower(), "is typically", char_align.lower() +".")
            check = str(input("Are you sure you wish to continue?   "))
            if check.lower() == "y" or check.lower() == "yes":
                pass
            else:
                team = char_align

        if team == winning_team:
            won = 1
        else:
            won = 0

        assigned_by = str(input("Enter how character was assigned (manual/model):   "))
        while assigned_by != "manual" and assigned_by != "model":
            print("Please enter a valid option")
            assigned_by = str(input("Enter how character was assigned (manual/model):   "))
            

        query = """
        INSERT INTO assignments (game_id, player_id, character_id, team, won, assigned_by)
        VALUES(?, ?, ?, ?, ?, ?);
        """


        cur.execute(query, (game_id, player_id, char_id, team, won, assigned_by))
        con.commit()
        logged_players += 1
        con.close()
        new_strength = compute_adjusted_strength(char_id)
        print(f"Character {char_id} → Adjusted Strength: {new_strength}")



    eloUpdate(game_id)





