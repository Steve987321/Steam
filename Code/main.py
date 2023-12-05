import SteamAPI
from GUI import Window


def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()


def test_steam_api():
    # voeg testen toe
    for i in SteamAPI.get_player_ID('76561198123041058'):
        a = SteamAPI.get_players_summaries(i)
        print(a)


def test_steamnaam():
    a = SteamAPI.get_player_ID('76561198123041058')
    print(a)


if __name__ == "__main__":
    # test_scherm()
    # test_steamnaam()
    test_steam_api()
