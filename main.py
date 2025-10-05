## MAIN PROGRAM ##

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpBinary
import sqlite3
from didyoumean3.didyoumean import did_you_mean



from calcs import assignments
from post_game_data_collection import dataCollection
from new_script import addScript



de = ["Liza", "Madi", "Ed", "Rowan", "Rita", "Aden", "Grace", "Aman", "Will"]

## Set up for a new game
def setup():
    no_script = True
    while no_script == True:
        script = str(input("Enter the name of a script or 'custom' or 'random':   "))

        words = script.strip().split()
        for i in range(0,len(words)):
            if i == 0:
                script = words[i].capitalize()
            elif 1 <= i and i < len(words):
                script += "_" + words[i].lower()
            else:
                script += words[i].lower()

        try:
            con = sqlite3.connect('clocktower.db') 
            cur = con.cursor() 
        except Exception as e:
            print(f'An error occurred: {e}.')
            exit()
        query = """
        SELECT *
        FROM scripts
        WHERE name = ?
        """
        print(script)
        cur.execute(query, (script,))
        script_exists = cur.fetchall()
        con.close()
        if script_exists == []:
            print("Script", script, "does not exist")
            add = str(input("Add " + script + " into the database?   ")).lower()
            if add == "yes" or add == "y":
                addScript(script)
                no_script = False
            
        else:
            no_script = False


    players = []
    inputting = True
    while inputting == True:
        player = str(input("Enter player name/ x (done) /add:   ")).capitalize()
        if player.lower() == "x":
            inputting = False
        elif player.lower() == "add":
            new_player = str(input("Enter player name:   "))
            addPlayer(new_player)
        elif player.lower() == "de":
            players = de
            inputting = False
        else:
            if player in players:
                print("Player already in game")
            else:
                try:
                    con = sqlite3.connect('clocktower.db') 
                    cur = con.cursor() 
                except Exception as e:
                    print(f'An error occurred: {e}.')
                    exit()
                query = """
                SELECT *
                FROM players
                WHERE name = ?
                """
                cur.execute(query, (player,))
                player_exists = cur.fetchall()
                con.close()
                print(player_exists)
                if player_exists != []:
                    players.append(player)
                else:
                    print("Player", player, "does not exist")
                    add = str(input("Add " + player + " into database?   ")).lower()
                    if add == "y" or add == "yes":
                        addPlayer(player)
                    
                    

    assignments(script, players)
    return players


## Adds a new player into the database
def addPlayer(player=None):
    if player == None:
        player = str(input("Enter player name:   ")).capitalize()
    try:
        con = sqlite3.connect('clocktower.db') 
        cur = con.cursor() 
    except Exception as e:
        print(f'An error occurred: {e}.')
        exit()
    query = """
    INSERT INTO players (name)
    VALUES(?);
    """
    cur.execute(query, (player,))
    con.commit() 
    con.close()
    print("Player", player, "was added")


## Adds the game results into the database
def gameResults():
    dataCollection()


## Main function 
def main():
    in_menu = True
    while in_menu == True:
        menu = str(input("""
A = Set up game
B = Add game results
C = Add new player
D = Add new script
X = Quit
    """))

        if menu.lower() == "a":
            setup()
        elif menu.lower() == "b":
            dataCollection()
        elif menu.lower() == "c":
            addPlayer()
        elif menu.lower() == "d":
            addScript()
        elif menu.lower() == "x":
            in_menu = False
        else:
            print("Please select a valid option")
    


main()
