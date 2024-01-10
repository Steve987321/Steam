import SteamAPI
import time
from GUI import Window
# from lcd_led_pico_code import pico_main

with open('steamid.txt', 'r+') as file:
    check = file.readlines()
    if not check:
        steam_id = input('What is your steamID? ')
        file.write(steam_id)
    else:
        steam_id = check[0].strip()
        #print(steam_id)


def test_steam_api():
    player = SteamAPI.Player(SteamAPI.Api.get_player_summary(steam_id))
    player_friends = player.get_friends()
    print("friends:", player_friends)
    print("name:", player.get_name())
    print("status:", player.get_status().name)
    print("game:", player.get_playing_game())
    print("avatar url:", player.get_avatar(SteamAPI.AvatarFormaat.KLEIN))

    pass

def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()

class ApiLoop:
    def test_steam_api(self):
        while True:
            friends = SteamAPI.get_player_friendsid(steam_id)
            #if friends is empty:
            # continue
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
                print(online_friends)

                test_steam_vriend_online = ["Damian"]
                test_steam_vriend_offline = ["Duncan"]
                test_steam_vriend_spel = ["Damian;THE FINALS"]
                # pico_main(test_steam_vriend_online, test_steam_vriend_offline, test_steam_vriend_spel)

            time.sleep(10)

if __name__ == "__main__":
    #test_steamnaam()
    test_steam_api()
    # test_scherm()