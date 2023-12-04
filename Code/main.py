from APICalls import SteamAPI
from GUI import Window

def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()


def test_steam_api():
    # voeg testen toe
    for i in SteamAPI.GetPleayerID('76561198123041058'):
        a = SteamAPI.GetPlayersSummaries(i)
        print(a)

def test_steamnaam():
    a = SteamAPI.GetPleayerID('76561198123041058')
    print(a)

if __name__ == "__main__":
    #test_scherm()
    #test_steamnaam()
    test_steam_api()