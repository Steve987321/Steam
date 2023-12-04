import requests
import json


class SteamAPI:

    # TODO: Ergens anders opslaan?
    KEY = "0CF13F9FBA5C093B11239F396170BD4D"

    def GetPlayerSummary(id: str | list[str]):
        """
        Geeft informatie van de speler/profiel door de gegeven SteamID.

        Args:
            id: Steam ID van de speler waar informatie van wordt opgehaald.
        Returns:
            ....
        """

        request = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={SteamAPI.KEY}&steamids={id}"
        response = requests.get(request)
        print(response)
        data = response.text
        data2 = json.loads(data)

        # req2 = f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={SteamAPI.KEY}&steamid=76561198123041058&format=json"

        return data2
