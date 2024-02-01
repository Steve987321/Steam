from lcd1602 import LCD
from machine import Pin
import time
import neopixel


# 25-1-2024 yes


def steam_uitlezer(st_lst_info, blink_not, cpy_of_lst):
    if len(st_lst_info) > 1:  # Checkt voor nieuwe info
        for item in st_lst_info:  # Zo ja:
            cpy_of_lst.append(item)  # Slaat het op in aparte lijsten om data_loss te voorkomen
            blink_not += 3  # Voegt 3 blinks toe per item
        blink_not = blink_not - 3
    return blink_not, cpy_of_lst  # Return de nieuwe variabelen


def blink_handler(blink_not, color, np):
    if blink_not > 0:  # Checkt of er geblink moet gebeuren
        while blink_not > 0:  # Voor elke:
            for i in range(1, 8):
                np[i] = color  # Blinkt voor de opgegeven kleur (groen, rood of blauw)
            np.write()
            time.sleep(0.2)

            for i in range(1, 8):
                np[i] = [0, 0, 0]  # Maakt de lampjes leeg zodat je een blink-effect krijgt
            np.write()
            time.sleep(0.2)

            blink_not -= 1
        time.sleep(0.8)
        return blink_not  # Return de nieuwe waardes terug naar de oude variabelen


def lcd_writer(regel_1, regel_2, st_info_lst, lcd):
    lcd.write(0, 0, regel_1)  # Schrijft Regel 1 op het lcd-scherm over
    lcd.write(0, 1, regel_2)  # Schrijft Regel 2 op het lcd-scherm over
    time.sleep(1)
    lcd.clear()
    time.sleep(1)
    st_info_lst.pop(0)  # Verwijdert de getoonde informatie zodat er een while-loop gebruikt kan worden


def pico_main(st_online_lst, st_offline_lst, st_game_lst, online_lst_cpy, offline_lst_cpy, game_lst_cpy):
    np = neopixel.NeoPixel(Pin(13), 8)  # Pin waar de Neopixel LED mee verbonden is
    lcd = LCD()
    switch_pin = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)  # Pin waar de knop mee verbonden is

    np[0] = [0, 255, 0]  # Maakt het eerste lampje groen om mee te beginnen
    np.write()

    groen = [0, 255, 0]
    rood = [255, 0, 0]
    blauw = [0, 0, 255]
    geel = [255, 255, 0]

    # not = notificatie
    blink_not_online = 0
    blink_not_offline = 0
    blink_not_game = 0

    blink_not_online, online_lst_cpy = steam_uitlezer(st_online_lst, blink_not_online, online_lst_cpy)
    blink_not_offline, offline_lst_cpy = steam_uitlezer(st_offline_lst, blink_not_offline, offline_lst_cpy)
    blink_not_game, game_lst_cpy = steam_uitlezer(st_game_lst, blink_not_game, game_lst_cpy)

    while blink_not_online > 0 or blink_not_offline > 0 or blink_not_game > 0:
        np[0] = geel  # Maakt het eerste lampje geel om aan te tonen dat er nieuwe informatie beschikbaar is
        np.write()
        print(online_lst_cpy)
        blink_not_online = blink_handler(blink_not_online, groen, np)
        blink_not_offline = blink_handler(blink_not_offline, rood, np)
        blink_not_game = blink_handler(blink_not_game, blauw, np)

    if len(online_lst_cpy) == 0 and len(offline_lst_cpy) == 0 and len(game_lst_cpy) == 0:
        np[0] = groen  # Maakt het lampje weer groen zodra er geen informatie beschikbaar is
        np.write()

    timer_lengte = 10
    start_time = time.time()  # Geef user 10 seconden om de button in te klikken, en wacht daarna weer op nieuwe data

    while time.time() - start_time < timer_lengte:
        if switch_pin.value() == 1:
            while len(online_lst_cpy) > 0 or len(offline_lst_cpy) > 0 or len(game_lst_cpy) > 0:
                if len(online_lst_cpy) > 0:
                    while len(online_lst_cpy) > 0:
                        if not online_lst_cpy[0] == '*****':
                            regel_1 = online_lst_cpy[0]
                            regel_2 = "is Online!"
                            lcd_writer(regel_1, regel_2, online_lst_cpy, lcd)
                        else:
                            online_lst_cpy.pop(0)
                    online_lst_cpy = []
                print(2)
                if len(offline_lst_cpy) > 0:
                    while len(offline_lst_cpy) > 0:
                        if not offline_lst_cpy[0] == '*****':
                            regel_1 = offline_lst_cpy[0]
                            regel_2 = "is Offline!"
                            lcd_writer(regel_1, regel_2, offline_lst_cpy, lcd)
                        else:
                            offline_lst_cpy.pop(0)
                    offline_lst_cpy = []
                if len(game_lst_cpy) > 0:
                    print(game_lst_cpy)
                    for item in game_lst_cpy:
                        print(item)
                        if not item == '*****':
                            naam, game = item.split(";")[0], item.split(";")[1]
                            regel_1 = f"{naam} speelt:"
                            regel_2 = f"{game}"
                            lcd.write(0, 0, regel_1)  # Schrijft Regel 1 op het lcd-scherm over
                            lcd.write(0, 1, regel_2)  # Schrijft Regel 2 op het lcd-scherm over
                            time.sleep(1)
                            lcd.clear()
                            time.sleep(1)
                    game_lst_cpy = []
            time.sleep(0.5)
    if len(online_lst_cpy) == 0 and len(offline_lst_cpy) == 0 and len(game_lst_cpy) == 0:
        np[0] = groen  # Maakt het lampje weer groen zodra er geen informatie beschikbaar is
        np.write()
    return online_lst_cpy, offline_lst_cpy, game_lst_cpy


online = []  # Kopie de info, zodat data-loss wordt voorkomen als de knop niet wordt ingedrukt en data wordt refresht
offline = []
spel = []

while True:
    data = input()  # Wacht om input van de pico-com code
    raw = eval(data)  # Veranderd de string naar code, aka naar een list met 3 lists erin
    vriend_online__list = raw[0]
    vriend_offline_list = raw[1]
    vriend_speelt__list = raw[2]

    pico_main(vriend_online__list, vriend_offline_list, vriend_speelt__list, online, offline, spel)
