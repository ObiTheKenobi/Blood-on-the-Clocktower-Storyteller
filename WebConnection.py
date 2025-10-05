from selenium import webdriver
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert

import pandas as pd
import time


# Sample data
assignments = [
    {'player': 'Alice',   'character': 'Clockmaker',     'win_probability': 0.72, 'team': 'Good'},
    {'player': 'Bob',     'character': 'Marionette',     'win_probability': 0.35, 'team': 'Evil'},
    {'player': 'Charlie', 'character': 'Monk',       'win_probability': 0.68, 'team': 'Good'},
    {'player': 'Dana',    'character': 'Exorcist',      'win_probability': 0.50, 'team': 'Neutral'},
    {'player': 'Eli',     'character': 'Empath',         'win_probability': 0.80, 'team': 'Good'},
    {'player': 'Faye',    'character': 'Godfather',            'win_probability': 0.40, 'team': 'Evil'},
    {'player': 'George',  'character': 'Fortune Teller', 'win_probability': 0.75, 'team': 'Good'},
    {'player': 'Hannah',  'character': 'Scarlet Woman',  'win_probability': 0.30, 'team': 'Evil'},
    {'player': 'Ian',     'character': 'Artist',    'win_probability': 0.65, 'team': 'Good'},
    {'player': 'Jade',    'character': 'Pukka',         'win_probability': 0.45, 'team': 'Evil'}
]

# Create the DataFrame
assignment_df = pd.DataFrame(assignments)


## Add a player into the grimoire
def addPlayer(driver, playerName): 
    ActionChains(driver)\
        .click(None)\
        .send_keys("a")\
        .perform()
    
        # Wait for the pop-up element to appear
    # Switch to the alert
    alert = Alert(driver)
    alert.send_keys(playerName)
    # Accept the alert
    alert.accept()


## Assign characters to players 
def assignPlayers(driver, assignments):
    players = driver.find_elements(By.CLASS_NAME, "player")

    for player in players:
        name = None

        try:
            name_span = player.find_element(By.CSS_SELECTOR, "div.name > span")
            name = name_span.text.strip()
        except:
            pass

        if name:
            match = assignments.loc[assignments['player'] == name, 'character']
            if not match.empty:
                character = match.iloc[0]
                try:
                    token = player.find_element(By.CLASS_NAME, "token")
                    driver.execute_script("arguments[0].click();", token)
                except Exception as e:
                    print(f"Could not click token for {name}: {e}")
            else:
                print(f"No character assignment found for {name}")
        else:
            print("Could not extract player name")


        character = str(assignments.loc[assignments['player'] == name, 'character'].values[0]).replace(" ", "")
  
        selector = f"div.token.{character.lower()}"
        char_token = driver.find_element(By.CSS_SELECTOR, selector)
        driver.execute_script("arguments[0].click();", char_token)

        print(f"{name} has been assigned a character")
        time.sleep(0.1)

        

## Main function
def webSetUp(assignments, script):
    options = Options()
    options.add_argument("--no-sandbox")  # Run in headless mode
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.get("https://clocktower.live/")

    disable_animations = driver.find_element(By.XPATH, "//li[contains(text(), 'Disable Animations')]")
    driver.execute_script("arguments[0].click();", disable_animations)

    ActionChains(driver)\
        .click(None)\
        .send_keys("ge")\
        .perform()

    if script == "Trouble_brewing":
        edition = driver.find_element(By.XPATH, "//li[contains(text(), 'Trouble Brewing')]")
        edition.click()
    elif script == "Sects_and_violets":
        edition = driver.find_element(By.XPATH, "//li[contains(text(), 'Sects & Violets')]")
        edition.click()
    elif script == "Bad_moon_rising":
        edition = driver.find_element(By.XPATH, "//li[contains(text(), 'Bad Moon Rising')]")
        edition.click()
    else:
        edition = driver.find_element(By.XPATH, "//li[contains(text(), 'Custom Script')]")
        edition.click()
        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept='application/json']")
        # Provide the full path to the file you want to upload
        file_input.send_keys(f"C:/JSON_BOTC/{script}.json")
    print("blerug")
    
    
    for player in assignments['player']:
        addPlayer(driver, player)
    assignPlayers(driver, assignment_df)




    time.sleep(3)

    ############# IMPORTANT TO HIDE THE ASSIGNMENTS FROM THE STORYTELLER
    ActionChains(driver)\
    .click(None)\
    .send_keys("g")\
    .perform()

    driver.quit()

script = "Uncertain_death"

webSetUp(assignment_df, script)