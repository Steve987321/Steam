import requests
import json


# TODO: Ergens anders opslaan?
KEY = "0CF13F9FBA5C093B11239F396170BD4D"


# def get_steam_summary(steam_id: str | list[str]):


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
        id_data = id_data_json['response']['players']
        return [name["personaname"] for name in id_data]

    # TODO: geef een foutmelding
    print(response)
    return ""


def get_player_friendsid(self: str | list[str]):
    request = f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={KEY}&steamid=76561198123041058&format=json"
    response = requests.get(request)
    data = response.text
    data2 = json.loads(data)

    IDdata = data2
    friends = IDdata['friendslist']['friends']

    steam_ids = [friend['steamid'] for friend in friends]

    return steam_ids
