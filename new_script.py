### NEW SCRIPT ###

import sqlite3

## Replace characters that are already in the script with another one
def editChars(char_list, char_names, char):
    print("Characters:")
    for i in range(0, len(char_names)):
        print(str(i + 1) + ".", char_names[i])
    remove_char = str(input("Enter the character to remove:   "))
    remove_char = " ".join(word.capitalize() for word in remove_char.split())
    if remove_char in char_names:
        remove = str(input("Replace " + remove_char + " with " + char[1] + "?   ")).lower()
        if remove == "y" or remove == "yes":
            print("Replaced \n")
            ind = char_names.index(remove_char)
            del char_names[ind]
            del char_list[ind]
            char_names.append(char[1])
            char_list.append(char[0])
        else:
            print("No character removed\n")
         


## Force in a character if it is necessary according to script logic
def forceChars(force_char_list, force_char_names, force_char, force_limit, orig_char_list, orig_char_names, orig_char):
    print("Characters:")
    for i in range(0, len(force_char_names)):
        print(str(i + 1) + ".", force_char_names[i])
    if not force_limit:
        add_replace = False
        while add_replace == False:
            add_char = str(input("Add the "+force_char[1]+"?   ")).lower()
            if add_char == "yes" or add_char == "y":
                force_char_names.append(force_char[1])
                force_char_list.append(force_char[0])
                return
            elif add_char == "no" or add_char == "n":
                replace = str(input("Replace a character with " + force_char[1]+ "?   ")).lower()
                if replace == "yes" or replace == "y":
                    add_replace = True
                else:
                    remove = str(input("Remove " + orig_char[1] + "?   ")).lower()
                    if remove == "yes" or remove == "y":
                        ind = orig_char_names.index(orig_char[1])
                        del orig_char_names[ind]
                        del orig_char_list[ind]
                        return False
                        
                    print("Please choose to add or replace")
            else:
                print("Please choose a valid option")
            
    remove_char = str(input("Enter the character to replace:   "))
    remove_char = " ".join(word.capitalize() for word in remove_char.split())
    if remove_char in orig_char_names:
        remove = str(input("Replace " + remove_char + " with " + force_char[1] + "?   ")).lower()
        if remove == "y" or remove == "yes":
            print("Replaced \n")
            ind = force_char_names.index(remove_char)
            del force_char_names[ind]
            del force_char_list[ind]
            force_char_names.append(force_char[1])
            force_char_list.append(force_char[0])
            return True
        else:
            print("No character removed\n")
    return False
    

## Ensures any scripts added contain the necessary limits for number of characters in certain roles
def scriptRequirements(script_id, script_type):
    try:
        con = sqlite3.connect('clocktower.db') 
        cur = con.cursor() 
    except Exception as e:
        print(f'An error occurred: {e}.')
        exit()
    not_done = True
    if script_type == "Full":
        towns = 10
        outs = 2
        minions = 2
    else:
        towns = 6
        outs = 2
        minions = 2

    
    print("SCRIPT REQUIREMENTS:")
    print("Townsfolk:", towns)
    print("Outsiders:", outs)
    print("Minions:", minions)
    print("Demons: 1")
    
    global towns_in 
    global outs_in
    global minions_in 
    global demons_in 

    towns_in = []
    t_names = []
    outs_in = []
    o_names = []
    minions_in = []
    m_names = []
    demons_in = []
    d_names = []
    not_force = True
    while not_done == True:
        char = str(input("Enter character name or done:   "))
        char = " ".join(word.capitalize() for word in char.split())
        if char == "Done":
            if len(towns_in) < towns:
                print("Not enough townsfolk -", towns - len(towns_in), "left to add\n")
                continue
            else:
                if len(outs_in) < outs:
                    print("Not enough outsiders -", outs - len(outs_in), "left to add\n")
                    continue
                else:
                    if len(minions_in) < minions:
                        print("Not enough minions -", minions - len(minions_in), "left to add\n")
                        continue
                    else:
                        if len(demons_in) < 1:
                            print("Not enough demons - 1 left to add\n")
                            continue
                        else:


                            if "Choirboy" in t_names and "King" not in t_names:
                                print("King must be included if there is a Choirboy")
                                if len(towns_in) == 15:
                                    limit = True
                                else:
                                    limit = False
                                temp = forceChars(towns_in, t_names, [35, "King"], limit, towns_in, t_names, [13, "Choirboy"])
                                not_force = False
                                if temp:
                                    not_done = False

                            elif "Huntsman" in t_names and "Damsel" not in o_names:
                                print("Damsel must be included if there is a Huntsman")
                                if len(outs_in) == 6:
                                    limit = True
                                else:
                                    limit = False
                                    temp = forceChars(outs_in, o_names, [72, "Damsel"], limit, towns_in, t_names, [31, "Huntsman"])
                                    not_force = False
                                    if temp:
                                        not_done = False
                                        ##13 4 4 4

                            else:
                                not_done = False
                      

        query = """
        SELECT character_id, role_type
        FROM characters
        WHERE name = ?
        """

        cur.execute(query, (char,))
        char_exists = cur.fetchall()
        if not_done and not_force:
            if char_exists == []:
                print("Invalid character name")
                continue
            
            char_id = char_exists[0][0]
            char_type = char_exists[0][1]

            if char_type == "Townsfolk":
                if char_id in towns_in:
                    print(char,"already in this script")
                elif len(towns_in) == 13:
                    print("Too many townsfolk")
                    edit = str(input("Would you like to change the townsfolk?   ")).lower()
                    if edit == "y" or edit == "yes":
                        editChars(towns_in, t_names, [char_id, char])
                    else:
                        print(char,"not added in")
                else:
                    towns_in.append(char_id)
                    t_names.append(char)
                    print("char",char)
                    if char == "Choirboy" and "King" not in t_names:
                        print("!! King is required if there is a Choirboy !!\n")
                    elif char == "Huntsman" and "Damsel" not in o_names:
                        print("!! Damsel is required if there is a Huntsman !!\n")
      
            elif char_type == "Outsider":
                if char_id in outs_in:
                    print(char,"already in this script")
                elif len(outs_in) == 6:
                    print("Too many outsiders")
                    edit = str(input("Would you like to change the outsiders?   ")).lower()
                    if edit == "y" or edit == "yes":
                        editChars(outs_in, o_names, [char_id, char])
                    else:
                        print(char,"not added in")
                else:
                    outs_in.append(char_id)
                    o_names.append(char)
                    
            elif char_type == "Minion":
                if char_id in minions_in:
                    print(char,"already in this script")            
                elif len(minions_in) == 6:
                    print("Too many minions")
                    edit = str(input("Would you like to change the minions?   ")).lower()
                    if edit == "y" or edit == "yes":
                        editChars(minions_in, m_names,[char_id, char])
                    else:
                        print(char,"not added in")
                else:
                    minions_in.append(char_id)
                    m_names.append(char)

            elif char_type == "Demon":
                if char_id in demons_in:
                    print(char,"already in this script")
                elif len(demons_in) == 5:
                    print("Too many demons")
                    edit = str(input("Would you like to change the demons?   ")).lower()
                    if edit == "y" or edit == "yes":
                        editChars(demons_in, d_names, [char_id, char])
                    else:
                        print(char,"not added in")

                else:
                    demons_in.append(char_id)
                    d_names.append(char)

    print("Script finished")
    for i in range(0, len(towns_in)):
        query = """
        INSERT INTO script_characters (script_id, character_id)
        VALUES(?, ?);
        """
        cur.execute(query, (script_id, towns_in[i],))
        

    for i in range(0, len(outs_in)):
        query = """
        INSERT INTO script_characters (script_id, character_id)
        VALUES(?, ?);
        """
        cur.execute(query, (script_id, outs_in[i],))
        

    for i in range(0, len(minions_in)):
        query = """
        INSERT INTO script_characters (script_id, character_id)
        VALUES(?, ?);
        """
        cur.execute(query, (script_id, minions_in[i],))

        
    for i in range(0, len(demons_in)):
        query = """
        INSERT INTO script_characters (script_id, character_id)
        VALUES(?, ?);
        """
        cur.execute(query, (script_id, demons_in[i],))
        con.commit()
    con.close()
    return


## Main function to add the new script into the database
def addScript(script_name=None):
    in_database = True
    while in_database == True:
        if script_name == None:
            script_name = str(input("Enter the name of the custom script:   "))
            
        try:
            con = sqlite3.connect('clocktower.db') 
            cur = con.cursor() 
        except Exception as e:
            print(f'An error occurred: {e}.')
            exit()



        words = script_name.strip().split()
        for i in range(0,len(words)):
            if i == 0:
                script_name = words[i].capitalize()
            elif 1 <= i and i < len(words):
                script_name += "_" + words[i].lower()
            else:
                script_name += words[i].lower()
                
        query = """
        SELECT *
        FROM scripts
        WHERE name = ?
        """


        cur.execute(query, (script_name,))
        script_exists = cur.fetchall()
        if script_exists != []:
            print("This script already exists")
            rename = str(input("Would you like to rename the script?   ")).lower()
            if rename == "y" or rename == "yes":
                script_name = None
            else:
                print("Cannot rewrite an existing script")
                print("Returning to menu")
                return
        else:
            in_database = False

    script_type = str(input("Is this a full script or a teensyville script?   ")).capitalize()
    while script_type != "Full" and script_type != "Teensyville":
        print("Please enter a valid script type \n")
        script_type = str(input("Is this a full script or a teensyville script?   ")).capitalize()
   
        

    query = """
    INSERT INTO scripts (name, type)
    VALUES(?, ?);
    """
    cur.execute(query, (script_name, script_type,))
    con.commit()
    script_id = cur.lastrowid
    con.close()


    scriptRequirements(script_id, script_type)

          


