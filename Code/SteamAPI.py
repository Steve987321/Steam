import requests
import json


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
        filtered_data = [name["personaname"] for status, name in zip(id_data, id_data) if status["personastate"] == 1]
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


def get_player_game(steam_id: str):
    """return string of game that the given steam id is playing"""
    # check steam id online status
    info = get_player_summary(steam_id)[0]
    if len(info) == 0:
        return ""

    try:
        game = info["gameextrainfo"]
    except KeyError as e:
        return ""

    return game
