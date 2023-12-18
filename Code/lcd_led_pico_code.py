from lcd1602 import LCD
from machine import *
import time
import neopixel

# STEAM INFO OPVRAGEN NOG FIXEN


np = neopixel.NeoPixel(machine.Pin(13), 8)
lcd = LCD()
switch_pin = Pin(19, Pin.IN, pull=Pin.PULL_DOWN)

np[0] = [0, 255, 0]
np.write()

steam_vriend_online = ["1"]
steam_vriend_offline = ["test"]
steam_vriend_spel = ["2"]

online_list = []
offline_list = []
spel_list = []

wit = [0, 0, 0]
groen = [0, 255, 0]
rood = [50, 0, 0]
blauw = [0, 0, 255]
geel = [255, 255, 0]

while True:
    blink_notificatie_online = 0
    blink_notificatie_offline = 0
    blink_notificatie_spel = 0

    if len(steam_vriend_online) > 0:
        for naam in steam_vriend_online:
            blink_notificatie_online += 3
            online_list.append(naam)

    if len(steam_vriend_offline) > 0:
        for naam in steam_vriend_offline:
            blink_notificatie_offline += 3
            offline_list.append(naam)

    if len(steam_vriend_spel) > 0:
        for spel in steam_vriend_spel:
            blink_notificatie_spel += 3
            spel_list.append(spel)

    while blink_notificatie_online > 0 or blink_notificatie_spel > 0 or blink_notificatie_offline > 0:
        np[0] = geel
        np.write()
        if blink_notificatie_online > 0:
            steam_vriend_online = []
            temp_value = blink_notificatie_online
            blink_notificatie_online = 0
            while temp_value > 0:
                for i in range(1, 8):
                    np[i] = groen
                np.write()
                time.sleep(0.2)

                for i in range(1, 8):
                    np[i] = wit
                np.write()
                time.sleep(0.2)

                temp_value -= 1
            time.sleep(0.8)
        elif blink_notificatie_offline > 0:
            steam_vriend_offline = []
            temp_value = blink_notificatie_offline
            blink_notificatie_offline = 0
            while temp_value > 0:
                for i in range(1, 8):
                    np[i] = rood
                np.write()
                time.sleep(0.2)

                for i in range(1, 8):
                    np[i] = wit
                np.write()
                time.sleep(0.2)

                temp_value -= 1
            time.sleep(0.8)
        elif blink_notificatie_spel > 0:
            steam_vriend_spel = []
            temp_value = blink_notificatie_spel
            blink_notificatie_spel = 0
            while temp_value > 0:
                for i in range(1, 8):
                    np[i] = blauw
                np.write()
                time.sleep(0.2)

                for i in range(1, 8):
                    np[i] = wit
                np.write()
                time.sleep(0.2)

                temp_value -= 1
            time.sleep(0.8)

    if len(online_list) == 0 and len(offline_list) == 0 and len(spel_list) == 0:
        np[0] = groen
        np.write()

    if switch_pin.value():
        while len(online_list) > 0 or len(offline_list) > 0 or len(spel_list) > 0:
            if len(online_list) > 0:
                while len(online_list) > 0:
                    regel_1 = online_list[0]
                    regel_2 = "is ONLINE!"
                    lcd.write(0, 0, regel_1)
                    lcd.write(0, 1, regel_2)
                    time.sleep(1)
                    lcd.clear()
                    time.sleep(1)
                    online_list.pop(0)
            if len(offline_list) > 0:
                while len(offline_list) > 0:
                    regel_1 = offline_list[0]
                    regel_2 = "is OFFLINE!"
                    lcd.write(0, 0, regel_1)
                    lcd.write(0, 1, regel_2)
                    time.sleep(1)
                    lcd.clear()
                    time.sleep(1)
                    offline_list.pop(0)
            if len(spel_list) > 0:
                while len(spel_list) > 0:
                    regel_1 = "test"
                    regel_2 = "SPEELT"
                    lcd.write(0, 0, regel_1)
                    lcd.write(0, 1, regel_2)
                    time.sleep(1)
                    lcd.clear()
                    time.sleep(1)
                    spel_list.pop(0)
        time.sleep(0.5)
