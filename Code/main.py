import SteamAPI
from GUI import Window


def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()


def test_steam_api():
    # voeg testen toe
    friends = SteamAPI.get_player_friendsid('76561198123041058')
    friends_names = SteamAPI.get_steamid_name(friends)
    print(friends_names)


def test_steamnaam():
    a = SteamAPI.get_steamid_name(['76561198123041058', "76561198181797231"])
    #print(a)
    a = SteamAPI.get_steamid_name(['76561198123041058'])
    #print(a)
    a = SteamAPI.get_steamid_name('76561198123041058')
    print(a)
    a = SteamAPI.get_player_summary('76561198123041058')
    print(a)
    a = SteamAPI.get_player_game('76561198123041058')
    print(a)


if __name__ == "__main__":
    # test_scherm()
    test_steamnaam()
    test_steam_api()
