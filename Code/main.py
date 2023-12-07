import SteamAPI
from GUI import Window

with open('steamid.txt', 'r+') as file:
    check = file.readlines()
    if not check:
        steam_id = input('What is your steamID? ')
        file.write(steam_id)
    else:
        steam_id = check[0].strip()
        #print(steam_id)


def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()


def test_steam_api():
    # voeg testen toe
    friends = SteamAPI.get_player_friendsid(steam_id)
    friends_statusses = SteamAPI.get_player_states(friends)
    online_friends = []
    for sid, status in friends_statusses.items():
        if status == SteamAPI.PlayerStatus.ONLINE:
            online_friends.append(sid)

    print("online friends:", online_friends)
    friends_names = SteamAPI.get_steamid_name(friends)
    #print(friends_names)

    a = SteamAPI.get_player_game(online_friends)
    print(a)
    a = SteamAPI.check_playerfriends_ingame(online_friends,steam_id)
    print(a)
def test_steamnaam():
    a = SteamAPI.get_steamid_name(steam_id)
    print(a)
    a = SteamAPI.get_player_summary(steam_id)
    print(a)
    a = SteamAPI.get_player_game(SteamAPI.get_player_friendsid(steam_id))
    print(a)
    a = SteamAPI.check_playerfriends_ingame(SteamAPI.get_player_friendsid(steam_id))
    print(a)


if __name__ == "__main__":
    # test_scherm()
    # test_steamnaam()
    test_steam_api()
