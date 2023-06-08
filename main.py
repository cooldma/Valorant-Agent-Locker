import json, time
import os
import sys

from valclient.client import Client
import difflib

print('Valorant Agent Locker [https://github.com/cooldma/Valorant-Agent-Locker/]')
valid = False
running = True
agent = {}
seenMatches = []
choice = ''
allAgents = ["jett", "reyna", "raze", "yoru", "phoenix", "neon", "breach", "skye", "sova", "kayo", "killjoy", "cypher",
             "sage", "chamber", "omen", "brimstone", "astra", "viper", "fade", "harbor", "gekko"]

# For developers
showErrors = False

def find_most_similar_string(string, arraylist):
    distances = []
    for other_string in arraylist:
        distances.append(difflib.SequenceMatcher(None, string, other_string).ratio())
    most_similar_string = arraylist[distances.index(max(distances))]
    return most_similar_string

# This is used for PyToExe for people who don't want to download everything manually
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


with open(resource_path('data.json'), 'r') as f:
    data = json.load(f)
    agent = data['agent']
    maps = data['maps']
    ranBefore = data['ran']
    mapCodes = data['codes']
    region = data['region']
    hoverDelay = data['hoverDelay']
    lockDelay = data['lockDelay']
    loopDelay = data['loopDelay']

if ranBefore:
    choice = input("type S to start or type C to change preferred agent: ").lower()

if ranBefore == False or choice == 'c':
    playerRegion = input('Enter your region (e.g. NA): ').lower()
    client = Client(region=playerRegion)
    client.activate()

    print("\nPlease enter your preferred agent.")
    print("_" * 80, end="\n")
    preAgent = input(f"Preferred agent: ").lower()
    preferredAgent = find_most_similar_string(preAgent, allAgents)
    print("Set preferred agent to: {}".format(preferredAgent))
    for map in maps.keys():
        valid = False
        while not valid:
            try:
                if preferredAgent in agent.keys():
                    maps[map] = agent[preferredAgent]
                    valid = True
                else:
                    print("Invalid Agent")
            except Exception as e:
                print("Input Error")

    with open('data.json', 'w') as f:
        data['maps'] = maps
        data['ran'] = True
        data['region'] = playerRegion
        json.dump(data, f)

else:
    client = Client(region=region)
    client.activate()
    print("Starting agent locker. Currently selected agent: " + list(agent.keys())[
        list(agent.values()).index(maps["ascent"])].capitalize())
print("Waiting for agent select screen\n")
while running:
    time.sleep(loopDelay)
    try:
        sessionState = client.fetch_presence(client.puuid)['sessionLoopState']
        matchID = client.pregame_fetch_match()['ID']
        if sessionState == "PREGAME" and matchID not in seenMatches:
            seenMatches.append(matchID)
            matchInfo = client.pregame_fetch_match(matchID)
            mapName = matchInfo["MapID"].split('/')[-1].lower()
            side = lambda teamID: "Defending" if teamID == "Blue" else "Attacking"

            print(f'Agent Select Found - {mapCodes[mapName].capitalize()} - ' + side(
                matchInfo['Teams'][0]['TeamID']) + ' first')
            if maps[mapName] is not None:
                time.sleep(hoverDelay)
                client.pregame_select_character(maps[mapName])
                time.sleep(lockDelay)
                client.pregame_lock_character(maps[mapName])
                print('Agent Locked - ' + list(agent.keys())[list(agent.values()).index(maps[mapName])].capitalize())
    except Exception as e:
        if "pre-game" not in str(e) and showErrors == True:
            print("An error occurred: ", e)