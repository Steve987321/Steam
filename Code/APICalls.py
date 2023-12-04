import requests
import json


class SteamAPI:

    # TODO: Ergens anders opslaan?
    KEY = "0CF13F9FBA5C093B11239F396170BD4D"

    def GetPlayersSummaries(id: str | list[str]):
        """
        Geeft informatie van de speler/profiel door de gegeven SteamID.

        Args:
            id: Steam ID van de speler waar informatie van wordt opgehaald.
        Returns:
            ....
        """
        request = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={SteamAPI.KEY}&steamids={id}"
        response = requests.get(request)
        return json.loads(response.text)
