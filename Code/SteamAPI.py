import requests
import json
import time
from enum import IntEnum


class PlayerStatus(IntEnum):
    INVALID = -1  # Iets is foutgegegaan
    OFFLINE = 0,  # speler is offline of heeft zijn profiel op private gezet
    ONLINE = 1,  # speler is online
    BUSY = 2,  # speler is busy
    AWAY = 3,  # speler is afk en away
    SNOOZE = 4,  # speler is afk
    LOOKING_TO_TRADE = 5,  # speler wilt traden
    LOOKING_TO_PLAY = 6  # speler wilt spelen


class AvatarFormaat(IntEnum):
    KLEIN = 0,      # 32x32
    MIDDEL = 1,     # 64x64
    GROOT = 2       # 184x184


try:
    with open("STEAM_API_KEY.txt") as key:
        KEY = key.readline()
        if KEY == "":
            print("Er is geen API key gevonden in STEAM_API_KEY.txt")
except FileNotFoundError:
    print("Er is geen STEAM_API_KEY.txt gevonden")


class Api:
    @staticmethod
    def get_json(request):
        response = requests.get(request)

        if response.ok:
            return response.json()
        else:
            print(f"[Steam API] response is niet ok: {response.status_code}, bij url: {request}")
            return ""

    @staticmethod
    def get_player_summary(steamid: str):
        request = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={KEY}&steamids={steamid}"
        return Api.get_json(request)

    @staticmethod
    def get_player_summaries(steamids: str | list):
        if isinstance(steamids, list):
            ids = ','.join(map(str, steamids))
        else:
            ids = steamids

        return Api.get_player_summary(ids)

    @staticmethod
    def get_player_friends(steamid):
        """Returns list of friends data"""
        request = f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={KEY}&steamid={steamid}&format=json"
        response = Api.get_json(request)

        friends = []
        try:
            for friend in response["friendslist"]["friends"]:
                friends.append(friend)
        except KeyError as e:
            print(f"[Steam API] fout bij ophalen vriendenlijst: {e}")

        return friends


class Player:
    def __init__(self, player_data):
        if "steamid" in player_data:
            self.data = player_data
        else:
            self.data = player_data["response"]["players"][0]

    def get_id(self) -> str:
        try:
            return self.data["steamid"]
        except KeyError as e:
            print(f"[Player] id kan niet worden gevonden: {e}")

    def get_name(self) -> str:
        """Return name as string """
        try:
            return self.data["personaname"]
        except KeyError as e:
            print(f"[Player] naam kan niet worden gevonden: {e}")

    def get_friends(self):
        """Geeft vrienden terug als lijst van Player objecten"""
        friends_data = Api.get_player_friends(self.get_id())
        friends_players = []
        friends_steamids = []

        if len(friends_data) == 0:
            return []

        for f in friends_data:
            try:
                friends_steamids.append(f["steamid"])
            except KeyError as e:
                print(f"[Player] steam id niet gevonden bij vriend: {e}")

        friend_summaries_response = Api.get_player_summaries(friends_steamids)
        for player_data in friend_summaries_response["response"]["players"]:
            friends_players.append(Player(player_data))

        return friends_players

    def get_status(self) -> PlayerStatus:
        """Return steam status """
        try:
            return PlayerStatus(int(self.data["personastate"]))
        except KeyError as e:
            print(f"[Player] naam kan niet worden gevonden: {e}")
        except ValueError as e:
            print(f"[Player] profile state is invalid: {e}")

        pass

    def get_avatar(self, formaat: AvatarFormaat) -> str:
        """Geeft url van avatar"""
        try:
            match formaat:
                case AvatarFormaat.KLEIN:
                    return self.data["avatar"]
                case AvatarFormaat.MIDDEL:
                    return self.data["avatarmedium"]
                case AvatarFormaat.GROOT:
                    return self.data["avatarfull"]
                case _:
                    opties = []
                    for f in AvatarFormaat:
                        opties.append(f.value)
                    print("[Player] geen geldige avatar formaat, kies uit: ", opties)
                    return ""

        except KeyError as e:
            print(f"[Player] avatar kan niet worden gevonden: {e}")
            return ""

    def get_playing_game(self) -> str:
        """Geeft naam van game die wordt gespeeld"""
        try:
            print(self.data['gameextrainfo'])
            return self.data["gameextrainfo"]
        except KeyError:
            #print("[Player] speler is niet in game")
            return ""
        pass


    def achievement(self) -> str:

        try:
            #print(self.data['gameid'])
            return self.data['gameid']
        except KeyError:
            return ""
        pass



import time

class SteamApi:
    def __init__(self, steam_id):
        self.steam_id = steam_id
        self.prev_online_friends = set()
        self.processed_game_ids = set()
        while True:
            self.check_and_print_changes()
            self.get_achievement(KEY,steam_id,2)
            self.get_games(KEY, steam_id)
            self.get_game_names(self.get_games(KEY, steam_id))
            time.sleep(2*++0)  # Adjust the delay time (in seconds) according to your needs

    # def player_Achievement(self):
    #     print(Api.get_player_summary(self.steam_id))

    def get_achievement(self, api_key, steam_id, app_id):
        player = Player(Api.get_player_summary(self.steam_id))
        app_id = player.achievement()
        if app_id and app_id not in self.processed_game_ids:
            self.processed_game_ids.add(app_id)  # Mark the game ID as processed
            url = f'https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/'
            params = {
                'key': api_key,
                'steamid': steam_id,
                'appid': app_id,
            }
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                #print(data.get('playerstats', {}).get('achievements', []))
            else:
                print(f"Error: {response.status_code}, {response.text}")

    def check_and_print_changes(self):
        player = Player(Api.get_player_summary(self.steam_id))
        print("name:", player.get_name())
        print("status:", player.get_status().name)
        print("game:", player.get_playing_game())
        player_friends = player.get_friends()
        current_online_friends = {friend.get_name() for friend in player_friends if friend.get_status() == PlayerStatus.ONLINE}

        # Check who went offline
        went_offline = self.prev_online_friends - current_online_friends
        if went_offline:
            print("Players who went offline:")
            for friend in went_offline:
                print(f'{friend}')

        # Check who came online
        came_online = current_online_friends - self.prev_online_friends
        if came_online:
            print("Players who came online:")
            for friend in came_online:
                print(f'{friend}')

        self.prev_online_friends = current_online_friends

    import requests
    def get_games(self, api_key, steam_id):
        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
        params = {
            'key': api_key,
            'steamid': steam_id,
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            games = data.get('response', {}).get('games', [])
            app_ids = [game.get('appid') for game in games]
            print(app_ids)
            return app_ids
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return []

    def get_game_names(self, app_ids):
        base_url = "https://store.steampowered.com/api/appdetails/"

        game_names = []

        for app_id in app_ids:
            if app_id in self.processed_game_ids:
                continue

            url = f"{base_url}?appids={app_id}"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                if data.get(str(app_id), {}).get("success", False):
                    game_name = data[str(app_id)]["data"]["name"]
                    game_names.append({"app_id": app_id, "game_name": game_name})
                    self.processed_game_ids.add(app_id)
                else:
                    print(f"Error: Game ID {app_id} not found")
            else:
                print(f"Error: Unable to retrieve data for Game ID {app_id}")

        for game_info in game_names:
            print(f"Game ID: {game_info['app_id']}, Game Name: {game_info['game_name']}")

        return game_names



    def test_api(self):

        pass












