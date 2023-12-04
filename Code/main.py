from APICalls import SteamAPI
from GUI import Window

def test_scherm():
    scherm = Window("Steam Train Groep", 500, 500)
    scherm.show()


def test_steam_api():
    # voeg testen toe
    a = SteamAPI.GetPlayersSummaries("76561198123041058")
    print(a)


if __name__ == "__main__":
    test_scherm()