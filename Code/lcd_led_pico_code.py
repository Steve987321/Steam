from lcd1602 import LCD
from machine import *
import time
import neopixel
# Hell yeah


def steam_uitlezer(steam_vriend_info, blink_notificatie, lijst):
    if len(steam_vriend_info) > 0:  # Checkt of er nieuwe informatie beschikbaar is van steam
        for item in steam_vriend_info:  # Zo ja:
            lijst.append(item)  # Slaat het nieuwe item op in de lijsten (online_list, offline_list of spel_list)
            blink_notificatie += 3  # Voegt 3 blinks toe per item
    return blink_notificatie  # Return de nieuwe variabele


def blink_handler(blink_notificatie, steam_vriend_info, color, np):
    if blink_notificatie > 0:  # Checkt of er geblinkt moet worden
        steam_vriend_info = []  # Herschrijft de lijst (LET OP, HIER MOET NOG OVER NAGEDACHT WORDEN)
        # WAARSCHIJNLIJK WORD ER BIJVOORBEELD ELKE 10 SECONDEN DEZE CODE AANGEROEPEMN MET NIEUWE STEAM INFO EN HOEFT
        # DEZE DUS NIET GECLEARED TE WORDEN
        while blink_notificatie > 0:
            for i in range(1, 8):
                np[i] = color  # Blinkt voor de opgegeven kleur (groen, rood of blauw)
            np.write()
            time.sleep(0.2)

            for i in range(1, 8):
                np[i] = [0, 0, 0]  # Maakt de lampjes leeg zodat je een blink-effect krijgt
            np.write()
            time.sleep(0.2)

            blink_notificatie -= 1
        time.sleep(0.8)
        return blink_notificatie, steam_vriend_info  # Return de nieuwe waardes terug naar de oude variabelen


def lcd_writer(regel_1, regel_2, steam_info_lijst, lcd):
    lcd.write(0, 0, regel_1)  # Schrijft Regel 1 op het lcd-scherm over
    lcd.write(0, 1, regel_2)  # Schrijft Regel 2 op het lcd-scherm over
    time.sleep(1)
    lcd.clear()
    time.sleep(1)
    steam_info_lijst.pop(0)  # Verwijdert de getoonde informatie zodat er een while-loop gebruikt kan worden


def main(steam_vriend_online, steam_vriend_offline, steam_vriend_spel):
    np = neopixel.NeoPixel(machine.Pin(13), 8)  # Pin waar de Neopixel LED mee verbonden is
    lcd = LCD()
    switch_pin = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)  # Pin waar de knop mee verbonden is

    np[0] = [0, 255, 0]  # Maakt het eerste lampje groen om mee te beginnen
    np.write()

    online_list = []   # Deze 3 lijsten worden gebruikt om steam info in op te slaan totdat deze worden ge-displayed op
    offline_list = []  # het LCD scherm
    spel_list = []

    # Alle kleuren die gebruikt worden
    wit = [0, 0, 0]
    groen = [0, 255, 0]
    rood = [50, 0, 0]
    blauw = [0, 0, 255]
    geel = [255, 255, 0]

    while True:
        blink_notificatie_online = 0  # Deze 3 variabelen worden gebruikt voor de blinks (elk item in steam info:
        blink_notificatie_offline = 0  # zorgt voor + 3, want blinkt 3 keer vòòr 1 item)
        blink_notificatie_spel = 0

        blink_notificatie_online = steam_uitlezer(steam_vriend_online, blink_notificatie_online, online_list)
        blink_notificatie_offline = steam_uitlezer(steam_vriend_offline, blink_notificatie_offline, offline_list)
        blink_notificatie_spel = steam_uitlezer(steam_vriend_spel, blink_notificatie_spel, spel_list)

        while blink_notificatie_online > 0 or blink_notificatie_spel > 0 or blink_notificatie_offline > 0:
            np[0] = geel  # Maakt het eerste lampje geel om aan te tonen dat er nieuwe informatie beschikbaar is
            np.write()

            blink_notificatie_online, steam_vriend_online = blink_handler(blink_notificatie_online, steam_vriend_online,
                                                                          groen, np)

            blink_notificatie_offline, steam_vriend_offline = blink_handler(blink_notificatie_offline,
                                                                            steam_vriend_offline, rood, np)

            blink_notificatie_spel, steam_vriend_spel = blink_handler(blink_notificatie_spel, steam_vriend_spel, blauw,
                                                                      np)

        if len(online_list) == 0 and len(offline_list) == 0 and len(spel_list) == 0:
            np[0] = groen  # Maakt het lampje weer groen zodra er geen informatie beschikbaar is
            np.write()

        if switch_pin.value():  # Laat één voor één de informatie op het lcd-scherm zien als je op het knopje klikt
            while len(online_list) > 0 or len(offline_list) > 0 or len(spel_list) > 0:
                if len(online_list) > 0:
                    while len(online_list) > 0:
                        regel_1 = online_list[0]
                        regel_2 = "is Online!"
                        lcd_writer(regel_1, regel_2, online_list, lcd)
                if len(offline_list) > 0:
                    while len(offline_list) > 0:
                        regel_1 = offline_list[0]
                        regel_2 = "is Offline!"
                        lcd_writer(regel_1, regel_2, offline_list, lcd)

                if len(spel_list) > 0:
                    while len(spel_list) > 0:
                        regel_1 = "Naam speelt"
                        regel_2 = "Spel"
                        lcd_writer(regel_1, regel_2, spel_list, lcd)
            time.sleep(0.5)


test_steam_vriend_online = ["Damian"]
test_steam_vriend_offline = ["Duncan"]
test_steam_vriend_spel = ["THE FINALS"]

main(test_steam_vriend_online, test_steam_vriend_offline, test_steam_vriend_spel)
