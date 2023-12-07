import SteamAPI
from GUI import Window

with open('steamid.txt', 'r+') as file:
    check = file.readlines()
    if not check:
        steam_id = input('What is your steamID? ')
        file.write(steam_id)
    else:
        steam_id = check[0].strip()
        print(steam_id)


def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()


def test_steam_api():
    # voeg testen toe
    friends = SteamAPI.get_player_friendsid(steam_id)
    friends_names = SteamAPI.get_steamid_name(friends)
    print(friends_names)


def test_steamnaam():
    a = SteamAPI.get_steamid_name(steam_id)
    print(a)
    a = SteamAPI.get_player_summary(steam_id)
    print(a)
    a = SteamAPI.get_player_game(SteamAPI.get_player_friendsid(steam_id))
    print(a)


if __name__ == "__main__":
    # test_scherm()
    test_steamnaam()
    test_steam_api()
