import requests
import json
import time
from enum import IntEnum
import threading


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
            return self.data["gameextrainfo"]
        except KeyError:
            #print("[Player] speler is niet in game")
            return ""
        pass


class SteamApiThread:
    def __init__(self, steam_id):
        self.has_data = False
        self.steam_id = steam_id
        self.prev_friends_status = {}
        self.prev_steamid_status = PlayerStatus.INVALID
        self.prev_steamid_game = None
        self.on_friend_list_change = None
        self.on_steamid_status_change = None
        self.stop = False

        self.player = None
        self.friends = []
        self.friends_online = []
        self.friends_offline = []
        self.friends_away = []
        self.friends_games = {}

        self.thread = threading.Thread(target=self.update)
        self.thread.start()

    def stop_thread(self):
        self.stop = True
        self.thread.join()

    def update(self):
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

                self.friends_games[friend.get_playing_game()] = friend

            self.friends_online += self.friends_away

            self.check_changes()
            self.has_data = True

            time.sleep(5)  # Adjust the delay time (in seconds) according to your needs

    def check_changes(self):
        player = Player(Api.get_player_summary(self.steam_id))
        status = player.get_status()
        game = player.get_playing_game()
        changed_player_list = []
        friend_status = {}
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

            friend_status[friend.get_name()] = friend.get_status()

        if len(self.prev_friends_status) == 0 and len(friend_status) > 0:
            changed_player_list = player.get_friends()
            changed = True

        if changed:
            self.on_friend_list_change(changed_player_list)

        self.prev_friends_status = friend_status
