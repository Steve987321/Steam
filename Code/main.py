from APICalls import SteamAPI


if __name__ == "__main__":
    a = SteamAPI.GetPlayerSummary("76561198123041058")
    print(a)
