import requests
import json
import time
from PIL import Image
from io import BytesIO
from enum import IntEnum
import threading
from multiprocessing.pool import ThreadPool


try:
    with open("STEAM_API_KEY.txt") as key:
        KEY = key.readline()
        if KEY == "":
            print("Er is geen API key gevonden in STEAM_API_KEY.txt")
except FileNotFoundError:
    print("Er is geen STEAM_API_KEY.txt gevonden")


class PlayerStatus(IntEnum):
    """Status van een Steam profiel"""
    INVALID = -1                # Iets is fout gegegaan
    OFFLINE = 0,                # speler is offline of heeft zijn profiel op private gezet
    ONLINE = 1,                 # speler is online
    BUSY = 2,                   # speler is busy
    AWAY = 3,                   # speler is afk en away
    SNOOZE = 4,                 # speler is afk
    LOOKING_TO_TRADE = 5,       # speler wilt traden
    LOOKING_TO_PLAY = 6         # speler wilt spelen


class AvatarFormaat(IntEnum):
    """Grootte van steam profiel avatar"""
    KLEIN = 0,      # 32x32
    MIDDEL = 1,     # 64x64
    GROOT = 2       # 184x184


class GameInfo:
    def __init__(self, data):
        self.data = data
        self.capsule_img = None
        self.header_img = None

    def get_capsule_img(self):
        if self.capsule_img is not None:
            return self.capsule_img

        image_data = requests.get(self.data["capsule_image"])
        if not image_data.ok:
            print("[GameInfo] capsule image data kon niet worden opgehaald")
            return None

        self.capsule_img = Image.open(BytesIO(image_data.content))
        return self.capsule_img

    def get_header_img(self):
        if self.header_img is not None:
            return self.header_img

        image_data = requests.get(self.data["header_image"])
        if not image_data.ok:
            print("[GameInfo] header image data kon niet worden opgehaald")
            return None

        self.header_img = Image.open(BytesIO(image_data.content))
        return self.header_img

    def get_name(self):
        return self.data["name"]

    def get_metacritic_score(self):
        if "metacritic" not in self.data:
            return None

        return int(self.data["metacritic"]["score"])

    def get_developers(self) -> list[str]:
        res = []
        for developer in self.data["developers"]:
            res.append(developer)
        return res

    def get_price(self) -> str:
        if self.data["is_free"]:
            return "Free"
        else:
            if "price_overview" not in self.data.keys():
                return "-"
            return self.data["price_overview"]["final_formatted"]

    def get_supported_platforms(self) -> list[str]:
        res = []
        for platform, supported in self.data["platforms"].items():
            if supported:
                res.append(platform)
        return res


class Api:
    """Steam API calls"""

    processed_game_ids = {}

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
        if len(response) == 0:
            return []

        friends = []
        try:
            for friend in response["friendslist"]["friends"]:
                friends.append(friend)
        except KeyError as e:
            print(f"[Steam API] fout bij ophalen vriendenlijst: {e}")

        return friends

    @staticmethod
    def get_player_games_data(steamid):
        """Geeft alle games van een speler met info"""
        url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
        base_url = "https://store.steampowered.com/api/appdetails/"
        game_data = {}

        params = {
            'key': KEY,
            'steamid': steamid,
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            games = data.get('response', {}).get('games', [])
            app_ids = [game.get('appid') for game in games]
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return

        def get_name(app_id: str, game_data):
            """Thread job

            Parameters:
                app_id: id van de game/applicatie
                game_data: dict waar opgehaalde data wordt opgeslagen
            """
            if app_id in Api.processed_game_ids.keys():
                game_data[app_id] = Api.processed_game_ids[app_id]
                return

            url = f"{base_url}?appids={app_id}"
            response = requests.get(url)

            if response.ok:
                data = response.json()
                if data.get(app_id, {}).get("success", False):
                    game_data[app_id] = GameInfo(data[app_id]["data"])
                    Api.processed_game_ids[app_id] = GameInfo(data[app_id]["data"])
                else:
                    print(f"Error: Game ID {app_id} not found")
            else:
                print(f"Error: Unable to retrieve data for Game ID {app_id}")

            return

        # een request voor elke game
        pool = ThreadPool()
        task_list_results = []
        for app_id in app_ids:
            task_list_results.append(pool.apply_async(get_name, args=(str(app_id), game_data)))

        for res in task_list_results:
            res.get()

        pool.close()

        return game_data


class Player:
    def __init__(self, player_data, game_list=None):
        if "steamid" in player_data:
            self.data = player_data
        else:
            self.data = player_data["response"]["players"][0]

        self.game_list = game_list

        self.avatar = None

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
        if len(friend_summaries_response) == 0:
            for _ in range(3):
                friend_summaries_response = Api.get_player_summaries(friends_steamids)
                if len(friend_summaries_response) > 0:
                    break

        if len(friend_summaries_response) == 0:
            print("Friend summaries kon niet worden opgehaald...")
            return []
        response = friend_summaries_response["response"]
        for player_data in response["players"]:
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

    def get_avatar(self, formaat: AvatarFormaat = AvatarFormaat.MIDDEL) -> Image:
        """Geeft Image van avatar"""
        if self.avatar is not None:
            return self.avatar

        url = None

        try:
            match formaat:
                case AvatarFormaat.KLEIN:
                    url = self.data["avatar"]
                case AvatarFormaat.MIDDEL:
                    url = self.data["avatarmedium"]
                case AvatarFormaat.GROOT:
                    url = self.data["avatarfull"]
                case _:
                    opties = []
                    for f in AvatarFormaat:
                        opties.append(f.value)
                    print("[Player] geen geldige avatar formaat, kies uit: ", opties)
                    return None
        except KeyError as e:
            print(f"[Player] avatar kan niet worden gevonden: {e}")
            return ""
        image_data = requests.get(url)
        if not image_data.ok:
            print("[Player] image data kon niet worden opgehaald")
            return None

        self.avatar = Image.open(BytesIO(image_data.content))
        return self.avatar

    def get_playing_game(self) -> str:
        """Geeft naam van game die wordt gespeeld"""
        try:
            return self.data["gameextrainfo"]
        except KeyError:
            return ""

    def get_game_list(self):
        return self.game_list


class AvatarLoadThread:
    """Laad en 'cached' avatars van spelers"""
    def __init__(self, avatars: dict):
        self.avatars = avatars
        self.thread = None

    def start(self):
        if self.thread is not None and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.update)
        self.thread.start()

    def join(self):
        self.thread.join()

    def is_alive(self):
        if self.thread is None:
            return False

        return self.thread.is_alive()

    def update(self):
        for player, image in self.avatars.copy().items():
            if image is not None:
                continue
            image = player.get_avatar(AvatarFormaat.MIDDEL)
            self.avatars[player] = image


class SteamApiThread:
    """Update en behoudt info over speler en vrienden"""
    def __init__(self, steam_id):
        self.has_data = False
        self.steam_id = steam_id
        self.prev_friends_status = {}
        self.prev_steamid_status = PlayerStatus.INVALID
        self.prev_steamid_game = None
        self.on_friend_list_change = None
        self.on_steamid_status_change = None
        self.stop = False
        self.once = False

        self.player = None
        self.friends = []
        self.friends_online = []
        self.friends_offline = []
        self.friends_away = []

        self.prev_online_friends = set()
        self.processed_game_ids = set()

        self.thread = threading.Thread(target=self.update)
        self.thread.start()

    def stop_thread(self):
        """Stop/Join update thread"""
        self.stop = True
        self.thread.join()

    def update(self):
        """Update speler- en vriendenlijst info"""
        while not self.stop:
            self.player = Player(Api.get_player_summary(self.steam_id))
            self.friends = self.player.get_friends()

            self.friends_online.clear()
            self.friends_offline.clear()
            self.friends_away.clear()

            for friend in self.friends:
                match friend.get_status():
                    case PlayerStatus.ONLINE:
                        self.friends_online.append(friend)
                    case PlayerStatus.OFFLINE:
                        self.friends_offline.append(friend)
                    case PlayerStatus.AWAY:
                        self.friends_away.append(friend)

            self.friends_online += self.friends_away
            if not self.has_data:
                self.on_friend_list_change(self.friends + [self.player])
            else:
                self.check_changes()

            self.has_data = True

            time.sleep(5)  # Adjust the delay time (in seconds) according to your needs

    def check_changes(self):
        player = Player(Api.get_player_summary(self.steam_id))
        status = player.get_status()
        game = player.get_playing_game()

        changed_player_list = []
        changed = False

        if status != self.prev_steamid_status or game != self.prev_steamid_game:
            self.on_steamid_status_change(status, game)

        self.prev_steamid_status = status
        self.prev_steamid_game = game

        for friend in player.get_friends():
            if friend.get_name() in self.prev_friends_status.keys():
                if self.prev_friends_status[friend.get_name()] != friend.get_status():
                    changed_player_list.append(friend)
                    changed = True

        if changed:
            self.on_friend_list_change(changed_player_list)

        self.prev_friends_status.clear()
        for friend in player.get_friends():
            self.prev_friends_status[friend.get_name()] = friend.get_status()
