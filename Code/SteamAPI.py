import requests
import json
import time
from enum import IntEnum


class PlayerStatus(IntEnum):
    INVALID = -1            # Iets is foutegegaan
    OFFLINE = 0,            # speler is offline of heeft zijn profiel op private gezet
    ONLINE = 1,             # speler is online
    BUSY = 2,               # speler is busy
    AWAY = 3,               # speler is afk en away
    SNOOZE = 4,             # speler is afk
    LOOKING_TO_TRADE = 5,   # speler wilt traden
    LOOKING_TO_PLAY = 6     # speler wilt spelen

try:
    with open("STEAM_API_KEY.txt") as key:
        KEY = key.readline()
        if KEY == "":
            print("Er is geen API key gevonden in STEAM_API_KEY.txt")
except FileNotFoundError:
    print("Er is geen STEAM_API_KEY.txt gevonden")


def get_steamid_name(steam_ids: str | list[str]):
    """Geeft informatie van de speler/profiel door de gegeven SteamID of ID's.

    Args:
        steam_ids: Steam ID's van de speler of spelers waar informatie van wordt opgehaald.
    Returns:
        lijst van string met een naam of namen van de gegeven steamID of ID's
    """
    if isinstance(steam_ids, list):
        # id list naar komma gesplitste string
        ids = ','.join(map(str, steam_ids))
    else:
        ids = steam_ids

    request = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={KEY}&steamids={ids}"
    response = requests.get(request)
    if response.ok:
        id_data_json = response.json()
        #print(id_data_json)
        id_data = id_data_json['response']['players']
        filtered_data = [name["personaname"] for name in id_data]
        return filtered_data

    # TODO: geef een foutmelding
    # print(response)
    return ""


def get_player_friendsid(steam_id: str):
    request = f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={KEY}&steamid={steam_id}&format=json"
    response = requests.get(request)
    data = response.text
    data2 = json.loads(data)

    IDdata = data2
    friends = IDdata['friendslist']['friends']

    steam_ids = [friend['steamid'] for friend in friends]

    return steam_ids


def get_player_summary(steam_ids: str | list[str]):
    if isinstance(steam_ids, list):
        ids = ','.join(map(str, steam_ids))
    else:
        ids = steam_ids

    request = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={KEY}&steamids={ids}"
    response = requests.get(request)
    if response.ok:
        id_data_json = response.json()
        return id_data_json

def get_player_game(steam_ids: str | list[str]):
    info = get_player_summary(steam_ids)
    players = info['response']['players']
    games = {}
    for p in players:
        playername = p["personaname"]
        try:
            games[playername] = p["gameextrainfo"]
        except KeyError:
            games[playername] = None

    return games



def get_player_states(steam_ids: str | list[str]):
    players = get_player_summary(steam_ids)["response"]["players"]

    statusses = {}

    for p in players:
        try:
            state_int = int(p["personastate"])
            id = p["steamid"]
        except ValueError:
            statusses[id] = PlayerStatus.INVALID
        except KeyError:
            statusses[id] = PlayerStatus.INVALID
        else:
            statusses[id] = PlayerStatus(state_int)

    return statusses


def check_playerfriends_ingame(steam_ids, steam_id: str | list[str]):
    infofriends = get_player_summary(steam_ids)
    infohost = get_player_summary(steam_id)

    host = infohost['response']['players']

    players = infofriends['response']['players']

    games = []

    for h in host:
        hostname = h["personaname"]
        try:
            hostgame = h["gameextrainfo"]
        except KeyError:
            continue

        for p in players:
            playername = p["personaname"]
            try:
                friendsgames = p["gameextrainfo"]
            except KeyError:
                continue

            if hostgame == friendsgames:
                games.append((hostname, playername))

    return games


with open('steamid.txt', 'r+') as file:
    check = file.readlines()
    if not check:
        steam_id = input('What is your steamID? ')
        file.write(steam_id)
    else:
        steam_id = check[0].strip()
        #print(steam_id)

# Initialize previous information
previous_online_friends = set()
previous_friends_names = set()
previous_game_info = {}
previous_ingame_info = {}

def test_steam_api():
    friends = get_player_friendsid(steam_id)
    friends_statusses = get_player_states(friends)
    online_friends = [sid for sid, status in friends_statusses.items() if
                      status == PlayerStatus.ONLINE]

    global previous_online_friends, previous_friends_names, previous_game_info, previous_ingame_info

    if (
            set(online_friends) != previous_online_friends or
            set(friends) != previous_friends_names
    ):
        # Print online friends and their names
        # print("Online friends:", online_friends)
        friends_names = get_steamid_name(friends)
        # print("Friends names:", friends_names)

        game_info = get_player_game(online_friends)
        if game_info != previous_game_info:
            print("Game information:", game_info)

        ingame_info = check_playerfriends_ingame(online_friends, steam_id)
        # print(ingame_info)
        if ingame_info != previous_ingame_info:
            print("In-game information:", ingame_info)

        previous_online_friends = set(online_friends)
        previous_friends_names = set(friends)
        previous_game_info = game_info
        previous_ingame_info = ingame_info

