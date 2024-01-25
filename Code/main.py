# from SteamAPI import api
# import time
# from GUI import Window
# import threading
# # from lcd_led_pico_code import pico_main
#
# with open('steamid.txt', 'r+') as file:
#     check = file.readlines()
#     if not check:
#         steam_id = input('What is your steamID? ')
#         file.write(steam_id)
#     else:
#         steam_id = check[0].strip()
#         #print(steam_id)
#
# def test_scherm():
#     scherm = Window("Steam Train Groep", 500, 500, steam_id)
#     scherm.show()
#
# def test_Steamapi():
#     api
#
# if __name__ == "__main__":
#     #test_steamnaam()
#     t1 = threading.Thread(target=test_scherm,)
#     t2 = threading.Thread(target=test_Steamapi,)
#
#     t1.start()
#     t2.start()
#
#     t1.join()
#     t2.join()
import SteamAPI
import time
from GUI import Window
import threading

# from lcd_led_pico_code import pico_main

with open('steamid.txt', 'r+') as file:
    check = file.readlines()
    if not check:
        steam_id = input('What is your steamID? ')
        file.write(steam_id)
    else:
        steam_id = check[0].strip()
        # print(steam_id)

def test_Steamapi():
    my_api_instance = SteamAPI.SteamApiThread(steam_id)
    my_api_instance.test_api()

if __name__ == "__main__":
    scherm = Window("Steam Train Groep", 500, 500, steam_id)
    scherm.show()
    scherm.steamAPIThread.stop_thread()
