import requests
import json


class SteamAPI:

    # TODO: Ergens anders opslaan?
    KEY = "0CF13F9FBA5C093B11239F396170BD4D"

    def GetPlayersSummaries(steam_ids: str | list[str]):
        """
        Geeft informatie van de speler/profiel door de gegeven SteamID.

        Args:
            id: Steam ID van de speler of spelers waar informatie van wordt opgehaald.
        Returns:
            ....
        """
        request = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={SteamAPI.KEY}&steamids={steam_ids}"
        response = requests.get(request)
        namedata = json.loads(response.text)
        friendsname = namedata['response']['players']

        steam_names = [friend['personaname'] for friend in friendsname]

        for steam_naam in steam_names:
            a= steam_naam
        return a

    def GetPleayerID(self: str | list[str]):
        request = f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={SteamAPI.KEY}&steamid=76561198123041058&format=json"
        response = requests.get(request)
        # print(response)
        data = response.text
        data2 = json.loads(data)
        # print(data2)

        IDdata = data2
        friends = IDdata['friendslist']['friends']

        steam_ids = [friend['steamid'] for friend in friends]

        # print("Steam IDs:")

        return steam_ids

