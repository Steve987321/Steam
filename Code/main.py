import SteamAPI
import time
from GUI import Window

# with open('steamapikey.txt', 'r+') as file:
#     check = file.readlines()
#     if not check:
#         KEY = input('What is your steamKEY? ')
#         file.write(KEY)
#     else:
#         KEY = check[0].strip()
#        api key aan vragen voor onthoud



def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()

import time


class ApiLoop:

    def test_steam_api(self):
        while True:
            friends = SteamAPI.get_player_friendsid(steam_id)
            friends_statusses = SteamAPI.get_player_states(friends)
            online_friends = [sid for sid, status in friends_statusses.items() if
                              status == SteamAPI.PlayerStatus.ONLINE]

            global previous_online_friends, previous_friends_names, previous_game_info, previous_ingame_info

            if (
                    set(online_friends) != previous_online_friends or
                    set(friends) != previous_friends_names
            ):
                # Print online friends and their names
                # print("Online friends:", online_friends)
                friends_names = SteamAPI.get_steamid_name(friends)
                # print("Friends names:", friends_names)

                game_info = SteamAPI.get_player_game(online_friends)
                if game_info != previous_game_info:
                    print("Game information:", game_info)

                ingame_info = SteamAPI.check_playerfriends_ingame(online_friends, steam_id)
                # print(ingame_info)
                if ingame_info != previous_ingame_info:
                    print("In-game information:", ingame_info)

                previous_online_friends = set(online_friends)
                previous_friends_names = set(friends)
                previous_game_info = game_info
                previous_ingame_info = ingame_info

            time.sleep(10)


test_scherm()

# if __name__ == "__main__":
#     #test_steamnaam()
#     #test_steam_api()
#     test_scherm()
